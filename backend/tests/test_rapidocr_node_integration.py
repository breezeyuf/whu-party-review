from datetime import date

from ai import parser, pipeline
from models import MaterialType, TimeNodeExtraction, SystemSetting
from tests.test_review_regressions import test_engine, case, material
from tests.test_rapidocr_review_fixes import make_scan, real_ocr


def test_real_scanned_pdf_persists_application_date_node(case,monkeypatch,tmp_path,real_ocr):
    c=case; m,v=material(c)
    path=make_scan(tmp_path,'pdf')
    monkeypatch.setattr(parser,'STORAGE_DIR',tmp_path)
    monkeypatch.setattr(parser,'ensure_storage',lambda:None)
    kind=c.db.query(MaterialType).filter(MaterialType.code=='APPLICATION_LETTER').one()
    m.type_id=kind.id; m.type_status='CONFIRMED'; v.stored_path=path.name
    c.db.get(SystemSetting,'ocr').value={'engine':'rapidocr','min_dpi':200,'timeout_s':120}
    c.db.flush()
    parsed=pipeline.parse_version(c.db,v.id,use_llm=False)
    assert v.parse_status=='DONE' and parsed.ocr_engine=='rapidocr'
    node=c.db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id==v.id,
        TimeNodeExtraction.node_code=='T02',TimeNodeExtraction.is_current.is_(True)).one()
    assert node.value_date==date(2026,9,15) and node.page_no==1 and node.bbox
