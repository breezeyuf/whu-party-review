from ai.classify import classify_material
from ai.extract import extract_fields
from security import fingerprint, mask_id_card, mask_phone, password_ok


class T:
    def __init__(self, code, name, kws, excl=None):
        self.id = 1
        self.code = code
        self.name = name
        self.title_keywords = kws
        self.exclude_keywords = excl or []
        self.is_active = True


def test_classify_declared_and_auto():
    declared = T("THOUGHT_REPORT", "思想汇报", ["思想汇报"])
    r = classify_material("任意", declared, [declared])
    assert r["type_source"] == "DECLARED" and r["type_confidence"] == 1.0
    r = classify_material("思想汇报\n敬爱的党组织", None, [declared])
    assert r["type_code"] == "THOUGHT_REPORT"
    assert r["type_status"] in ("AUTO", "NEEDS_CONFIRM")


def test_extract_fields():
    text = "入党申请书\n敬爱的党组织：\n姓名：张三\n性别：女\n此致\n敬礼！\n申请人：张三\n2023年3月15日"
    f = extract_fields(text)
    assert f.get("title") == "入党申请书"
    assert f.get("signature_date") == "2023-03-15"


def test_security_helpers():
    assert mask_phone("13812345678") == "138****5678"
    assert "*" in (mask_id_card("420106199901011234") or "")
    assert password_ok("abc")
    assert password_ok("Abcdefg1") is None
    assert fingerprint("a", "b") == fingerprint("a", "b")
