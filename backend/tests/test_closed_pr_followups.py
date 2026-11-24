"""Regression coverage for the two open follow-ups recorded in closed PR #11."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from threading import Barrier
from types import SimpleNamespace

import pytest
from sqlalchemy.orm import Session

from ai.checks.timeline import run_timeline
from models import Material, MaterialVersion, RuleVersion, TimeNodeDef, TimeNodeExtraction
from services.rules import update_and_snapshot
from services.timeline import merge_archive_nodes, node_map_for_archive
from tests.pg_fixtures import make_schema_engine
from utils import now


@pytest.fixture(scope="module")
def published_schema():
    schema = make_schema_engine("ruleconc")
    try:
        yield schema
    finally:
        schema.drop()


def test_two_administrators_publish_serial_snapshots(published_schema):
    with Session(published_schema.engine) as db:
        base = db.query(RuleVersion).order_by(RuleVersion.version_no.desc()).first().version_no
        code = db.query(TimeNodeDef).filter(TimeNodeDef.code == "T01").one().code
    both_loaded = Barrier(2)
    actor = SimpleNamespace(id=None, role="ORG_ADMIN")

    def publish(field, value):
        with Session(published_schema.engine, expire_on_commit=False) as db:
            row = db.query(TimeNodeDef).filter(TimeNodeDef.code == code).one()
            both_loaded.wait(timeout=15)
            _, number = update_and_snapshot(db, actor, "time-nodes", row, {field: value}, field)
            db.commit()
            return number

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(publish, "name", "并发名称")
        second = pool.submit(publish, "sort_order", 919)
        numbers = {first.result(timeout=30), second.result(timeout=30)}
    assert numbers == {base + 1, base + 2}
    with Session(published_schema.engine) as db:
        versions = db.query(RuleVersion).filter(RuleVersion.version_no.in_(numbers)).order_by(RuleVersion.version_no).all()
        assert len(versions) == 2
        final = next(row for row in versions[-1].snapshot["time_node_defs"] if row["code"] == code)
        assert final["name"] == "并发名称" and final["sort_order"] == 919
        assert {versions[0].change_summary, versions[1].change_summary} == {"name", "sort_order"}


def test_r_t21_uses_each_version_upload_day_and_keeps_source(published_schema):
    from tests.pg_fixtures import build_case

    with Session(published_schema.engine, expire_on_commit=False) as db:
        c = build_case(db)
        from models import MaterialType
        source_type = db.query(MaterialType).filter_by(code='AUTOBIOGRAPHY').one()
        material = Material(archive_id=c.arch_a.id, submission_id=c.sub_branch.id, stage_code=1,
                            type_id=source_type.id, title="日期材料", status="ACTIVE", created_at=now(), updated_at=now())
        db.add(material)
        db.flush()
        version = MaterialVersion(material_id=material.id, version_no=1, original_filename="date.pdf",
                                  stored_path=f"date-{material.id}.pdf", file_ext="pdf", mime_type="application/pdf",
                                  file_size=1, sha256="0" * 64, parse_status="DONE",
                                  uploaded_at=datetime(2026, 1, 1, 18, 30, tzinfo=timezone.utc))
        db.add(version)
        db.flush()
        material.current_version_id = version.id
        db.add(TimeNodeExtraction(archive_id=c.arch_a.id, node_code="T01", material_id=material.id,
                                  material_version_id=version.id, seq_index=0, value_date=date(2026, 1, 3),
                                  page_no=2, bbox=[1, 2, 3, 4], method="RULE", is_current=True, created_at=now()))
        db.flush()
        merge_archive_nodes(db, c.arch_a.id)
        nodes = node_map_for_archive(db, c.arch_a.id)
        source = nodes["T01"]["sources"][0]
        assert source["upload_date"] == "2026-01-02"  # UTC midnight converted to Beijing day
        _, drafts, results = run_timeline(db, c.sub_branch, nodes)
        issue = next(d for d in drafts if d.rule_code == "R-T21")
        assert issue.material_version_id == version.id
        assert issue.location["page_no"] == 2 and issue.location["bbox"] == [1, 2, 3, 4]
        assert issue.expected_value == "≤ 2026-01-02"
        assert next(r for r in results if r["rule_code"] == "R-T21")["result"] == "FAIL"
        db.rollback()


def test_r_t21_multiple_sources_and_unknown_upload_date():
    rule = SimpleNamespace(code="R-T21", name="日期核验", applies_stages=[1],
                           params={"checks": [{"op": "valid_date", "nodes": "*"}]},
                           severity="BLOCK", message_template=None, basis=None)
    rules = SimpleNamespace(rows=lambda group: [rule])
    submission = SimpleNamespace(stage_code=1)
    context = SimpleNamespace(calendar={}, today=date(2026, 10, 26))
    sources = [
        {"node_code": "T06", "material_id": 1, "version_id": 11, "seq_index": 0,
         "date": "2026-01-03", "end_date": None, "upload_date": "2026-01-02"},
        {"node_code": "T06", "material_id": 2, "version_id": 12, "seq_index": 1,
         "date": "2026-01-04", "end_date": None, "upload_date": "2026-01-05"},
    ]
    node = {"T06": {"date": "2026-01-03", "seq": ["2026-01-03", "2026-01-04"], "sources": sources}}
    snapshot, drafts, results = run_timeline(None, submission, node, rule_set=rules, context=context)
    assert len(drafts) == 1 and drafts[0].material_version_id == 11
    assert snapshot["date_inputs"] == sources
    assert results[0]["result"] == "FAIL"
    sources[0]["upload_date"] = None
    _, drafts, results = run_timeline(None, submission, node, rule_set=rules, context=context)
    assert not drafts and results[0]["result"] == "SKIPPED"
