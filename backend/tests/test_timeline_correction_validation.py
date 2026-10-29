"""Canonical dates and explicit clearing cannot silently discard corrections."""
from models import ArchiveTimeNode, AuditLog, TimeNodeExtraction
from tests.test_review_regressions import case, test_engine, as_client
import pytest


@pytest.mark.parametrize("patch", [
    {"date": "2026-W01-1"}, {"date": "2026-01-05", "end_date": "2026-W02-1"},
    {"date": "20260105"}, {"date": "2026-1-05"},
    {"date": "2026-01-05", "clear": "false"},
    {"clear": "true"}, {"clear": None}, {"clear": 0}, {"clear": 1},
    {"clear": []}, {"clear": {}},
])
def test_invalid_date_or_clear_preserves_node_sources_and_audit(case, as_client, patch):
    c = case
    client = as_client(c.reviewer)
    endpoint = f"/api/archives/{c.arch.id}/timeline/T02"
    assert client.put(endpoint, json={"date": "2026-01-05", "reason": "核对原件"}).status_code == 200
    node = c.db.query(ArchiveTimeNode).filter_by(archive_id=c.arch.id, node_code="T02").one()
    old_time = c.arch.timeline_updated_at
    source_ids = [e.id for e in c.db.query(TimeNodeExtraction).filter_by(
        archive_id=c.arch.id, node_code="T02", is_current=True,
    ).all()]
    audit_count = c.db.query(AuditLog).filter_by(action="NODE_CORRECTION", object_id=str(c.arch.id)).count()

    response = client.put(endpoint, json={**patch, "reason": "再次核对"})
    assert response.status_code == 422, response.text
    c.db.refresh(node)
    c.db.refresh(c.arch)
    assert node.corrected_date.isoformat() == "2026-01-05"
    assert node.correction_reason == "核对原件"
    assert c.arch.timeline_updated_at == old_time
    assert [e.id for e in c.db.query(TimeNodeExtraction).filter_by(
        archive_id=c.arch.id, node_code="T02", is_current=True,
    ).all()] == source_ids
    assert c.db.query(AuditLog).filter_by(action="NODE_CORRECTION", object_id=str(c.arch.id)).count() == audit_count


def test_boolean_false_updates_date_and_true_explicitly_clears(case, as_client):
    c = case
    client = as_client(c.reviewer)
    endpoint = f"/api/archives/{c.arch.id}/timeline/T02"
    response = client.put(endpoint, json={"date": "2024-02-29", "clear": False, "reason": "核对闰日原件"})
    assert response.status_code == 200, response.text
    node = c.db.query(ArchiveTimeNode).filter_by(archive_id=c.arch.id, node_code="T02").one()
    assert node.corrected_date.isoformat() == "2024-02-29"
    response = client.put(endpoint, json={"clear": True, "reason": "撤销校正"})
    assert response.status_code == 200, response.text
    c.db.refresh(node)
    assert node.corrected_date is None and node.corrected_end_date is None and node.corrected_hours is None
    assert c.db.query(TimeNodeExtraction).filter_by(
        archive_id=c.arch.id, node_code="T02", method="MANUAL", is_current=True,
    ).count() == 0
    last = c.db.query(AuditLog).filter_by(action="NODE_CORRECTION", object_id=str(c.arch.id)).order_by(AuditLog.id.desc()).first()
    assert last.detail["clear"] is True
