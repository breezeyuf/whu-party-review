from services.workflow import _handover_ok


class R:
    def __init__(self, status, rec=None):
        self.handover_status = status
        self.effective_recommendation = rec


def test_handover_gate():
    assert not _handover_ok(None)
    assert not _handover_ok(R("REQUIRED"))
    assert _handover_ok(R("NOT_REQUIRED", "SUGGEST_PASS"))
    assert _handover_ok(R("DONE", "SUGGEST_RETURN"))
    assert _handover_ok(R("NOT_REQUIRED"))
