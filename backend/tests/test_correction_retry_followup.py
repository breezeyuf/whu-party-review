"""Repeating a save or parse must preserve already reviewed evidence."""
from copy import deepcopy
from datetime import date

import pytest

from ai import pipeline
from ai.extract import extract_fields
from ai.ocr import OCRProcessingError
from models import ParseResult, TimeNodeExtraction
from tests.test_review_regressions import case, test_engine, as_client, parsed_material
from utils import now


@pytest.mark.parametrize('edited_text', ['姓名：文本姓名', '姓名：新文本名'])
def test_repeated_text_save_preserves_existing_manual_field(case, as_client, edited_text):
    c=case; m,v=parsed_material(c)
    parsed=c.db.query(ParseResult).filter(ParseResult.version_id==v.id).one()
    parsed.full_text='姓名：旧识别名'
    parsed.corrected_text='姓名：文本姓名'
    parsed.extracted_fields=extract_fields(parsed.full_text)
    parsed.corrected_fields={**extract_fields(parsed.corrected_text),'name':'人工确认名','custom':'核实值'}
    c.db.flush()
    body={'version_id':v.id,'corrected_text':edited_text,'corrected_fields':deepcopy(parsed.corrected_fields)}
    for _ in range(2):
        response=as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed',json=body)
        assert response.status_code==200,response.text
        c.db.refresh(parsed)
        assert parsed.corrected_fields['name']=='人工确认名'
        assert parsed.corrected_fields['custom']=='核实值'
        body['corrected_fields']=deepcopy(parsed.corrected_fields)
    assert parsed.full_text=='姓名：旧识别名'


def test_repeated_text_save_preserves_deliberate_field_removal(case, as_client):
    c=case; m,v=parsed_material(c)
    parsed=c.db.query(ParseResult).filter(ParseResult.version_id==v.id).one()
    parsed.full_text=parsed.corrected_text='姓名：文本姓名'
    fields=extract_fields(parsed.corrected_text); fields.pop('name')
    parsed.corrected_fields=fields; c.db.flush()
    response=as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed',json={
        'version_id':v.id,'corrected_text':parsed.corrected_text,'corrected_fields':fields})
    assert response.status_code==200,response.text
    c.db.refresh(parsed)
    assert 'name' not in parsed.corrected_fields


def test_ocr_retry_failure_preserves_previous_parse_and_manual_evidence(case, monkeypatch):
    c=case; m,v=parsed_material(c)
    parsed=c.db.query(ParseResult).filter(ParseResult.version_id==v.id).one()
    parsed.full_text='原始成功全文'; parsed.corrected_text='人工校正全文'
    parsed.corrected_fields={'name':'人工姓名'}; parsed.extracted_fields={'name':'原姓名'}
    parsed.visual_marks={'anchors':[{'slot':'签名'}]}
    before=deepcopy(parsed.pages)
    ex=c.add(TimeNodeExtraction,archive_id=c.arch.id,node_code='T02',material_id=m.id,
             material_version_id=v.id,value_date=date(2026,1,1),method='MANUAL',is_current=True,created_at=now())
    c.db.flush()
    monkeypatch.setattr(pipeline,'parse_version_file',lambda *a:{'ocr_failed':True,'parser':'OCR',
        'full_text':'只有部分新文字','pages':[],'page_count':1})
    with pytest.raises(OCRProcessingError):
        pipeline.parse_version(c.db,v.id,use_llm=False)
    c.db.refresh(parsed); c.db.refresh(ex)
    assert v.parse_status=='FAILED' and '此前解析及人工校正已保留' in v.parse_error
    assert parsed.full_text=='原始成功全文' and parsed.pages==before
    assert parsed.extracted_fields=={'name':'原姓名'} and parsed.visual_marks['anchors']
    assert parsed.corrected_text=='人工校正全文' and parsed.corrected_fields=={'name':'人工姓名'}
    assert v.page_count==2 and ex.is_current and ex.method=='MANUAL'


def _fake_parse(monkeypatch, extractions):
    monkeypatch.setattr(pipeline,'parse_version_file',lambda *a:{'parser':'PDF_TEXT','full_text':'重新识别全文','pages':[]})
    monkeypatch.setattr(pipeline,'extract_nodes',lambda *a:deepcopy(extractions))


def test_successful_retry_preserves_manual_nodes_without_duplicate_automatic_value(case, monkeypatch):
    c=case; m,v=parsed_material(c)
    ex=c.add(TimeNodeExtraction,archive_id=c.arch.id,node_code='T02',material_id=m.id,
             material_version_id=v.id,value_date=date(2026,1,2),method='MANUAL',is_current=True,created_at=now())
    _fake_parse(monkeypatch,[{'node_code':'T02','value_date':date(2026,1,1)},
                             {'node_code':'T06','value_date':date(2026,2,1)}])
    pipeline.parse_version(c.db,v.id,use_llm=False)
    c.db.refresh(ex)
    rows=c.db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id==v.id,
                                             TimeNodeExtraction.is_current.is_(True)).all()
    assert ex.is_current and ex.value_date==date(2026,1,2)
    assert [(r.id,r.method) for r in rows if r.node_code=='T02']==[(ex.id,'MANUAL')]
    assert any(r.node_code=='T06' and r.method=='RULE' for r in rows)


def test_retry_does_not_restore_manually_deleted_node_and_later_creation_survives(case, as_client, monkeypatch):
    c=case; m,v=parsed_material(c)
    ex=c.add(TimeNodeExtraction,archive_id=c.arch.id,node_code='T02',material_id=m.id,
             material_version_id=v.id,value_date=date(2026,1,1),method='RULE',is_current=True,created_at=now())
    client=as_client(c.reviewer); url=f'/api/materials/{m.id}/parsed'
    response=client.put(url,json={'version_id':v.id,'reason':'识别错误，移除此来源',
                                 'extractions':[{'extraction_id':ex.id,'delete':True}]})
    assert response.status_code==200,response.text
    _fake_parse(monkeypatch,[{'node_code':'T02','value_date':date(2026,1,1)}])
    pipeline.parse_version(c.db,v.id,use_llm=False)
    assert not c.db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id==v.id,
          TimeNodeExtraction.node_code=='T02',TimeNodeExtraction.is_current.is_(True)).all()
    response=client.put(url,json={'version_id':v.id,'reason':'对照原件后新增正确日期',
                                 'extractions':[{'node_code':'T02','date':'2026-01-03'}]})
    assert response.status_code==200,response.text
    pipeline.parse_version(c.db,v.id,use_llm=False)
    rows=c.db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id==v.id,
          TimeNodeExtraction.node_code=='T02',TimeNodeExtraction.is_current.is_(True)).all()
    assert len(rows)==1 and rows[0].method=='MANUAL' and rows[0].value_date==date(2026,1,3)
