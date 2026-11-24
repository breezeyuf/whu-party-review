from types import SimpleNamespace as N
from ai.suggest import fill_suggestions
from ai.types import IssueDraft

class Rules:
    def rows(self, name):
        return [N(rule_code="R-T22",code="test",template_text="请核对《{材料名}》中的日期",example_text=None)]

def test_submission_suggestion_never_renders_an_empty_book_title():
    draft=IssueDraft(category="TIME",severity="BLOCK",rule_code="R-T22",title="阶段日期",description="缺少日期")
    fill_suggestions(None,[draft],rule_set=Rules())
    assert draft.suggestion=="请核对本次提交材料中的日期"
    named=IssueDraft(category="TIME",severity="BLOCK",rule_code="R-T22",title="阶段日期",description="缺少日期")
    fill_suggestions(None,[named],extra={"material_name":"入党申请书"},rule_set=Rules())
    assert named.suggestion=="请核对《入党申请书》中的日期"
