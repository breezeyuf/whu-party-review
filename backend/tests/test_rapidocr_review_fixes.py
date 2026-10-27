"""PR #30/#31 regressions: real scan text reaches time-node extraction."""
from datetime import date
from types import SimpleNamespace as N
from unittest.mock import Mock

import pytest

from ai import ocr, parser, enrichment
from ai.dates import find_dates
from ai.extract import extract_nodes


def make_scan(tmp_path, ext):
    import fitz
    with fitz.open() as document:
        page=document.new_page(width=500,height=180)
        page.insert_text((30,65),'虚构学生 申请日期',fontname='china-s',fontsize=22)
        page.insert_text((30,115),'2026年9月15日',fontname='china-s',fontsize=26)
        image=page.get_pixmap(dpi=200,alpha=False).tobytes('png')
    path=tmp_path/f'scan.{ext}'
    if ext=='png':
        path.write_bytes(image)
    else:
        with fitz.open() as scan:
            scan.new_page(width=500,height=180).insert_image(fitz.Rect(0,0,500,180),stream=image)
            scan.save(path)
    return path


def parse_scan(monkeypatch,tmp_path,path):
    monkeypatch.setattr(parser,'STORAGE_DIR',tmp_path)
    monkeypatch.setattr(parser,'ensure_storage',lambda:None)
    token=ocr.settings.set({'engine':'rapidocr','min_dpi':200,'timeout_s':120})
    try:
        return parser.parse_version_file(path.name,path.suffix.lstrip('.'))
    finally:
        ocr.settings.reset(token)


def assert_node_and_location(result):
    assert result['parser']=='OCR' and not result['ocr_failed']
    hits=find_dates(result['full_text'])
    assert any(hit['date']==date(2026,9,15) for hit in hits)
    material_type=N(date_node_map={'signature_date':'T02'})
    nodes=extract_nodes(result['full_text'],result['pages'],material_type,[])
    node=next(n for n in nodes if n['node_code']=='T02')
    assert node['value_date']==date(2026,9,15) and node['page_no']==1 and node['bbox']
    assert node['raw_text'] in result['pages'][0]['blocks'][-1]['text']


@pytest.mark.parametrize('raw', ['申请日期 ２ 0 ２ ６ 年9 月15 日','申请日期 2 0 2 6 - 0 9 - 1 5'])
def test_spaced_fullwidth_scan_date_reaches_node_with_original_evidence(monkeypatch,tmp_path,raw):
    pool=Mock()
    pool.submit.return_value.result.return_value=([(raw,[10,20,900,100],0.9)],None)
    monkeypatch.setattr(ocr,'_pool',lambda:pool)
    monkeypatch.setattr(ocr,'available_engines',lambda:['rapidocr'])
    result=parse_scan(monkeypatch,tmp_path,make_scan(tmp_path,'pdf'))
    assert_node_and_location(result)
    assert result['pages'][0]['blocks'][0]['raw_text']==raw


@pytest.fixture(scope='module')
def real_ocr():
    if not ocr.available_engines():
        pytest.skip('install backend/requirements-ocr.txt for real RapidOCR inference')
    yield
    ocr.shutdown()


@pytest.mark.parametrize('ext',['pdf','png'])
def test_real_scanned_fixture_produces_date_node(monkeypatch,tmp_path,real_ocr,ext):
    result=parse_scan(monkeypatch,tmp_path,make_scan(tmp_path,ext))
    assert_node_and_location(result)


@pytest.mark.parametrize('ext',['pdf','png'])
@pytest.mark.parametrize('engine,failed',[('auto',False),('none',False),('rapidocr',True)])
def test_optional_missing_engine_manual_fallback_vs_explicit_failure(monkeypatch,tmp_path,engine,failed,ext):
    monkeypatch.setattr(ocr,'available_engines',lambda:[])
    monkeypatch.setattr(parser,'STORAGE_DIR',tmp_path)
    monkeypatch.setattr(parser,'ensure_storage',lambda:None)
    path=make_scan(tmp_path,ext)
    token=ocr.settings.set({'engine':engine})
    try:
        result=parser.parse_version_file(path.name,ext)
    finally:
        ocr.settings.reset(token)
    assert result['ocr_failed'] is failed
    assert result['warnings'] and result['preview_pdf_path'] and result['page_count']==1


def test_only_rapidocr_discovered_and_legacy_selection_upgrades(monkeypatch):
    import importlib.util
    monkeypatch.setattr(importlib.util,'find_spec',lambda name:object())
    assert ocr.available_engines()==['rapidocr']
    assert ocr.configured_engine({'engine':'paddleocr'})=='rapidocr'


def test_shared_settings_probe(monkeypatch):
    from services import settings
    monkeypatch.setattr(settings,'get_setting',lambda *a:{'engine':'rapidocr','min_dpi':200})
    probe=Mock(return_value={'ok':True,'message':'synthetic result'})
    monkeypatch.setattr(ocr,'probe',probe)
    assert settings.test_ai(None,'ocr')['ok']
    probe.assert_called_once_with({'engine':'rapidocr','min_dpi':200})


def test_removed_engine_cannot_be_newly_configured():
    from errors import AppError
    from services import settings
    with pytest.raises(AppError):
        settings.update_settings(Mock(),N(role='SYS_ADMIN'),{'ocr':{'engine':'paddleocr'}})


def test_crashed_ocr_worker_is_reset_and_next_call_recovers(monkeypatch):
    from concurrent.futures.process import BrokenProcessPool
    monkeypatch.setattr(ocr,'available_engines',lambda:['rapidocr'])
    pool=Mock()
    pool.submit.return_value.result.side_effect=[BrokenProcessPool(),([('恢复',[0,0,1,1],1)],None)]
    monkeypatch.setattr(ocr,'_pool',lambda:pool)
    reset=Mock()
    monkeypatch.setattr(ocr,'_reset_pool',reset)
    pix=N(samples=b'',width=1,height=1,n=3)
    assert '异常退出' in ocr.ocr_pixmap(pix)[3]
    assert ocr.ocr_pixmap(pix)[0]=='恢复'
    reset.assert_called_once()


def test_reset_forces_stubborn_native_worker_to_exit(monkeypatch):
    pool=Mock(); process=Mock()
    pool._processes={1:process}
    process.is_alive.side_effect=[True,True]
    monkeypatch.setattr(ocr,'_POOL',pool)
    ocr._reset_pool()
    process.terminate.assert_called_once()
    process.kill.assert_called_once()
    assert process.join.call_count==2 and ocr._POOL is None
    pool.shutdown.assert_called_once_with(wait=False,cancel_futures=True)


def test_normalization_does_not_join_lines_or_change_original_non_ocr_dates():
    assert ocr.normalize_ocr_text('第1\n2页')=='第1\n2页'
    text='正文\n2026年9月15日'
    hit=find_dates(text)[0]
    assert text[hit['start']:hit['end']]=='2026年9月15日'


def test_suggestion_budget_and_duplicate_reuse_keep_rule_templates(monkeypatch):
    from ai import llm
    monkeypatch.setattr(llm,'llm_config',lambda db:{'desensitize':False})
    call=Mock(return_value=({'suggestion':'请核对原文。并提供说明。'},None,1))
    monkeypatch.setattr(enrichment,'chat_json',call)
    drafts=[N(category='CONTENT',suggestion='请核对原文。',description=f'问题{i}') for i in range(20)]
    enrichment.polish_suggestions(None,drafts)
    assert call.call_count==5
    assert all(d.suggestion=='请核对原文。' for d in drafts[5:])
    call.reset_mock()
    duplicates=[N(category='CONTENT',suggestion='请核对原文。',description='相同问题') for _ in range(20)]
    enrichment.polish_suggestions(None,duplicates)
    assert call.call_count==1
    assert all(d.suggestion==duplicates[0].suggestion for d in duplicates)
