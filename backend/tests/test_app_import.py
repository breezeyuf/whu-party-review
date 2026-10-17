import os


def test_import_main_app():
    os.environ["WORKER_ENABLED"] = "0"
    from main import app

    spec = app.openapi()
    paths = spec.get("paths") or {}
    assert "/api/health" in paths
    assert "/api/auth/login" in paths
    assert "/api/meta" in paths
    assert "/api/archives" in paths
    assert "/api/reports/{rid}/handover" in paths
    assert "/api/admin/seed-demo" in paths
    assert len(paths) >= 90
