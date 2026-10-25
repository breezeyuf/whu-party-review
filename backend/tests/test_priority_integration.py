from copy import deepcopy
from types import SimpleNamespace as N
from models import Archive, Submission, Material, MaterialVersion, ParseResult, User, MaterialType
from tests.test_review_regressions import case, test_engine, material, as_client, parsed_material
from utils import now


def test_batch_similarity_compares_other_students_only(case):
    from ai.similarity import batch_candidates, compare_batch
    c=case
    m,v=material(c)
    m.type_id=c.db.query(MaterialType).first().id; c.db.flush()
    # Duplicate archive/submission with a different real user in the same batch.
    user=User(username='other-similarity',password_hash='unused',real_name='其他学生',org_id=c.branches[0].id,
              is_active=True,must_change_password=False,created_at=now(),updated_at=now())
    c.db.add(user); c.db.flush()
    archive=Archive(student_user_id=user.id,student_no='OTHER',real_name='其他学生',college_id=c.arch.college_id,
                    branch_id=c.branches[0].id,batch_id=c.sub.batch_id,current_stage=1,status='ACTIVE',anon_code='other-test',
                    created_at=now(),updated_at=now())
    c.db.add(archive); c.db.flush()
    sub=Submission(archive_id=archive.id,stage_code=c.sub.stage_code,batch_id=c.sub.batch_id,
                   college_id=c.sub.college_id,branch_id=c.sub.branch_id,status='DRAFT',created_at=now(),updated_at=now())
    c.db.add(sub); c.db.flush()
    other=Material(archive_id=archive.id,submission_id=sub.id,stage_code=sub.stage_code,title='other',type_id=m.type_id,
                   status='ACTIVE',version_count=1,created_at=now(),updated_at=now())
    c.db.add(other); c.db.flush()
    version=MaterialVersion(material_id=other.id,version_no=1,original_filename='other.pdf',stored_path='other.pdf',
                            file_ext='pdf',mime_type='application/pdf',file_size=1,sha256='f'*64,parse_status='DONE',uploaded_at=now())
    c.db.add(version); c.db.flush(); other.current_version_id=version.id
    parsed=ParseResult(version_id=version.id,parser='PDF_TEXT',full_text='这是用于同批次相似度验证的虚构文本',char_count=20,
                       pages=[],created_at=now(),updated_at=now())
    c.db.add(parsed); c.db.flush()
    assert [row[0] for row in batch_candidates(c.db,c.sub,m)]==[other.id]
    assert compare_batch(c.db,c.sub,m,parsed.full_text,0.8)['score']==1
    sub.batch_id=c.batches[1].id; c.db.flush()
    assert list(batch_candidates(c.db,c.sub,m))==[]
    sub.batch_id=c.sub.batch_id; other.status='DELETED'; c.db.flush()
    assert list(batch_candidates(c.db,c.sub,m))==[]


def test_text_correction_rederives_fields_when_ui_fields_untouched(case,as_client):
    c=case; m,v=parsed_material(c)
    p=c.db.query(ParseResult).filter(ParseResult.version_id==v.id).one()
    p.full_text='姓名：旧名字'; p.extracted_fields={'name':'旧名字','char_count':6}; c.db.flush()
    response=as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed',json={
        'version_id':v.id,'corrected_text':'姓名：新名字','corrected_fields':p.extracted_fields})
    assert response.status_code==200,response.text
    c.db.refresh(p)
    assert p.corrected_fields['name']=='新名字' and p.full_text=='姓名：旧名字'


def test_reparse_is_authorized_deduplicated_and_preserves_corrections(case,as_client):
    c=case; m,v=parsed_material(c)
    assert as_client(c.student).post(f'/api/materials/{m.id}/retry-parse').status_code==403
    c.sub.status='DRAFT'; c.db.flush()
    first=as_client(c.student).post(f'/api/materials/{m.id}/retry-parse')
    assert first.status_code==200,first.text
    second=as_client(c.student).post(f'/api/materials/{m.id}/retry-parse')
    assert first.json()['data']==second.json()['data']
    c.db.refresh(v); assert v.parse_status=='PENDING'
    v.is_frozen=True; c.db.flush()
    assert as_client(c.student).post(f'/api/materials/{m.id}/retry-parse').status_code==409


def test_failed_ocr_keeps_partial_result_and_failed_state(case,monkeypatch):
    import pytest
    from ai import pipeline
    from ai.ocr import OCRProcessingError
    c=case; m,v=material(c)
    monkeypatch.setattr(pipeline,'parse_version_file',lambda *a:{'ocr_failed':True,'full_text':'部分文字','parser':'OCR','pages':[]})
    with pytest.raises(OCRProcessingError): pipeline.parse_version(c.db,v.id,use_llm=False)
    assert v.parse_status=='FAILED'
    assert c.db.query(ParseResult).filter(ParseResult.version_id==v.id).one().full_text=='部分文字'


def test_retention_confirmation_preserves_original_and_is_idempotent(case,as_client,tmp_path):
    from dateutil.relativedelta import relativedelta
    from models import AuditLog
    c=case; m,v=material(c)
    original=tmp_path/'original.pdf'; original.write_bytes(b'original evidence')
    v.stored_path=str(original); v.uploaded_at=now()-relativedelta(years=11); c.db.flush()
    url='/api/settings/retention/materials'
    assert as_client(c.student).get(url).status_code==403
    data=as_client(c.org).get(url).json()['data']
    assert [row['id'] for row in data['items']]==[v.id]
    for _ in range(2):
        response=as_client(c.org).post(f'{url}/{v.id}/keep',json={'reason':'继续保留'})
        assert response.status_code==200,response.text
    assert original.read_bytes()==b'original evidence'
    assert c.db.query(AuditLog).filter(AuditLog.action=='RETENTION_KEEP').count()==1
    assert as_client(c.org).get(url).json()['data']['total']==0
    assert as_client(c.org).get(url+'?status=confirmed').json()['data']['total']==1
