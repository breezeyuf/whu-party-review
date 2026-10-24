from datetime import timedelta
from io import BytesIO
from types import SimpleNamespace as NS
import threading
import time
import pytest
from openpyxl import Workbook
from sqlalchemy.orm import Session
from tests.test_review_regressions import case, test_engine, material, as_client, parsed_material
from models import Message, Job, User, Archive, ExportFile
from utils import now


def workbook(branch, birth='2004-01-01'):
    wb=Workbook(); ws=wb.active; ws.title='学生档案'
    ws.append(['student_no','real_name','branch_code','birth_date','T01'])
    ws.append(['90001','虚构测试',branch,birth,'2026-01-01'])
    buf=BytesIO(); wb.save(buf); return buf.getvalue()


def test_import_preview_checks_scope_and_dates_without_writes(case):
    from services.importer import import_users_xlsx
    c=case; c.branches[0].code='TEST_BRANCH'; c.db.flush()
    counts=(c.db.query(User).count(),c.db.query(Archive).count())
    for branch,birth in [('missing','2004-01-01'),('TEST_BRANCH','2026-02-30')]:
        result=import_users_xlsx(c.db,c.org,workbook(branch,birth),True)
        assert result['errors'] and result['valid']==0
    assert counts==(c.db.query(User).count(),c.db.query(Archive).count())
    good=workbook('TEST_BRANCH')
    assert import_users_xlsx(c.db,c.org,good,True)['valid']==1
    assert import_users_xlsx(c.db,c.org,good,False)['created_archives']==1


def test_deadline_scope_dedup_and_returned_student(case):
    from services.deadlines import scan_deadlines
    c=case; c.batches[0].branch_deadline=now().date()+timedelta(days=3); c.db.flush()
    assert scan_deadlines(c.db)==1
    assert scan_deadlines(c.db)==0
    msg=c.db.query(Message).filter(Message.msg_type=='DEADLINE').one()
    assert msg.user_id==c.reviewer.id
    c.sub.status='RETURNED'; c.sub.return_level='BRANCH'; c.db.flush()
    assert scan_deadlines(c.db)==1
    assert c.db.query(Message).filter(Message.user_id==c.student.id,Message.msg_type=='DEADLINE').count()==1
    c.batches[0].status='CLOSED'; c.db.flush()
    assert scan_deadlines(c.db,now().date()+timedelta(days=2))==0


def test_versions_link_reports_and_recheck_changes(case,as_client):
    from ai.pipeline import run_check
    c=case; m,v=material(c)
    c.report.material_versions=[{'material_id':m.id,'version_id':v.id,'version_no':1}]
    c.db.flush()
    rows=as_client(c.org).get(f'/api/materials/{m.id}/versions').json()['data']
    assert rows[0]['report_ids']==[c.report.id]
    m.status='DELETED'; c.db.flush()
    report=run_check(c.db,c.sub.id,'RECHECK',c.org.id,use_llm=False)
    assert report.changed_materials==[{'material_id':m.id,'old_version_id':v.id,'new_version_id':None,'change':'REMOVED'}]
    assert as_client(c.org).get(f'/api/reports/{report.id}').json()['data']['changed_materials']==report.changed_materials


def test_heartbeat_commits_during_work(test_engine,monkeypatch):
    import worker
    monkeypatch.setattr(worker,'SessionLocal',lambda:Session(test_engine))
    with Session(test_engine) as db:
        job=Job(job_type='PARSE',status='RUNNING',created_at=now(),heartbeat_at=now()-timedelta(minutes=1))
        db.add(job); db.commit(); jid=job.id
    stopped=threading.Event(); t=threading.Thread(target=worker._pulse,args=(jid,stopped,0.05)); t.start()
    try:
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            with Session(test_engine) as db:
                if db.get(Job,jid).heartbeat_at > now()-timedelta(seconds=3): break
            time.sleep(0.05)
        else: pytest.fail('Heartbeat did not commit')
    finally:
        stopped.set(); t.join(2)
        with Session(test_engine) as db:
            db.query(Job).filter(Job.id==jid).delete(); db.commit()


def test_ocr_pixel_coordinates_map_to_pdf(monkeypatch):
    import fitz
    from ai import ocr
    from ai.parser import _ocr_page
    monkeypatch.setattr(ocr,'ocr_pixmap',lambda pix:('test',[{'text':'test','bbox':[0,0,pix.width,pix.height],'conf':1}],'rapidocr',None))
    doc=fitz.open(); page=doc.new_page(width=600,height=800)
    try:
        assert _ocr_page(page)[1][0]['bbox']==[0,0,600,800]
    finally: doc.close()


def test_model_extraction_rejects_invented_evidence(monkeypatch):
    from ai import enrichment
    answer={'dates':[{'node_code':'T01','date':'2026-01-01','raw_text':'不存在的片段','confidence':0.99}]}
    monkeypatch.setattr(enrichment,'chat_json',lambda *a,**kw:(answer,None,1))
    nodes=[NS(code='T01',name='申请日期',value_kind='DATE')]
    assert enrichment.extract_fallback(None,'申请日期2026年1月1日',[],[],nodes)[0]==[]
    answer['dates'][0]['raw_text']='申请日期2026年1月1日'
    assert enrichment.extract_fallback(None,'申请日期2026年1月1日',[],[],nodes)[0][0]['method']=='LLM'


def test_model_classification_unknown_code_falls_back(monkeypatch):
    from ai import enrichment
    original={'type_source':'AI','type_confidence':0.1,'type_status':'NEEDS_CONFIRM'}
    types=[NS(id=1,code='APPLICATION',name='申请书',is_active=True)]
    answer={'type_code':'UNKNOWN','confidence':0.99,'reason':'test'}
    monkeypatch.setattr(enrichment,'chat_json',lambda *a,**kw:(answer,None,1))
    assert enrichment.classify_fallback(None,'正文',original,types,0.7)[0]==original
    answer['type_code']='APPLICATION'
    assert enrichment.classify_fallback(None,'正文',original,types,0.7)[0]['type_status']=='AUTO'


def test_suggestion_must_preserve_requirement(monkeypatch):
    from ai import enrichment, llm
    from ai.types import IssueDraft
    draft=IssueDraft(category='CONTENT',severity='WARN',title='test',description='test',suggestion='请核对原文。')
    monkeypatch.setattr(llm,'llm_config',lambda db:{'desensitize':False})
    answer={'suggestion':'直接通过。'}
    monkeypatch.setattr(enrichment,'chat_json',lambda *a,**kw:(answer,None,1))
    enrichment.polish_suggestions(None,[draft]); assert draft.suggestion=='请核对原文。'
    answer['suggestion']='请核对原文。并提交核对说明。'
    enrichment.polish_suggestions(None,[draft]); assert draft.suggestion==answer['suggestion']


def test_model_concurrency_limit(monkeypatch):
    from ai import llm
    active=0; peak=0; lock=threading.Lock()
    monkeypatch.setattr(llm,'llm_config',lambda db:{'max_concurrency':1})
    def request(*args,**kwargs):
        nonlocal active,peak
        with lock: active+=1; peak=max(peak,active)
        time.sleep(0.04)
        with lock: active-=1
        return {},None,1
    monkeypatch.setattr(llm,'_chat_json',request)
    threads=[threading.Thread(target=llm.chat_json,args=(None,'TEST',{})) for _ in range(4)]
    for thread in threads: thread.start()
    for thread in threads: thread.join(2)
    assert peak==1 and all(not thread.is_alive() for thread in threads)


def test_expired_export_file_removed(case,tmp_path,monkeypatch):
    import worker
    from services import storage
    monkeypatch.setattr(storage,'STORAGE_DIR',tmp_path)
    monkeypatch.setattr(storage,'ensure_storage',lambda:None)
    path=tmp_path/'exports'/'old.xlsx'; path.parent.mkdir(); path.write_bytes(b'test')
    case.add(ExportFile,export_type='DESENSITIZED_DATA',params={},file_name='old.xlsx',stored_path='exports/old.xlsx',
        created_at=now()-timedelta(days=2),expires_at=now()-timedelta(days=1))
    worker._scan(case.db); case.db.flush()
    assert not path.exists() and case.db.query(ExportFile).count()==0
