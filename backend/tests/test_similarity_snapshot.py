from hashlib import sha256
import json
from types import SimpleNamespace as N

from ai import similarity
from ai.checks.content import run_content


def test_comparison_records_scores_and_fingerprints_without_other_text(monkeypatch):
    other_text = "这是另一位学生提交的测试材料内容"
    monkeypatch.setattr(similarity, "batch_candidates", lambda *args: iter([(8, 18, other_text)]))
    submission = N(batch_id=1)
    compared = similarity.compare_batch(None, submission, N(id=1), other_text, 0.8)
    assert compared["score"] == 1.0
    assert compared["count"] == 1
    evidence = compared["comparison"]
    assert evidence["algorithm"] == "char_3gram_jaccard"
    assert evidence["candidates"] == [{"text_sha256": sha256(other_text.encode()).hexdigest(), "score": 1.0}]
    assert other_text not in str(evidence)
    assert "material_id" not in str(evidence) and "version_id" not in str(evidence)


def test_rule_result_keeps_original_comparison_after_corpus_changes(monkeypatch):
    own_text = "这是一份足够长的相似度测试材料内容"
    candidate = [own_text]
    monkeypatch.setattr(similarity, "batch_candidates", lambda *args: iter([(8, 18, candidate[0])]))
    rule = N(code="R-C10", category="CONTENT", engine="RULE", params={"threshold": 0.8},
             applies_to=[], is_active=True, name="相似度", severity="WARN",
             needs_human_judgement=True, basis="", message_template="")
    rules = N(rows=lambda group: [rule] if group == "check_rules" else [])
    material = N(id=1, status="ACTIVE", type_id=1, title="材料")
    version = N(id=11)
    parsed = N(full_text=own_text, corrected_text=None)
    submission = N(batch_id=1, archive_id=1, archive=N(student_user_id=1))

    def evaluate():
        return run_content(None, submission, [material], {1: version}, {11: parsed}, {}, False, rule_set=rules)

    first_issues, first_results = evaluate()
    stored = json.loads(json.dumps(first_results[0]["comparison_snapshot"][0]))
    assert first_issues and first_results[0]["result"] == "FAIL"
    assert stored["score"] == 1.0 and stored["threshold"] == 0.8
    candidate[0] = "完全不同的一份虚构材料"
    second_issues, second_results = evaluate()
    assert not second_issues and second_results[0]["result"] == "PASS"
    assert stored["score"] == 1.0
    assert stored != second_results[0]["comparison_snapshot"][0]
    assert stored["score"] >= stored["threshold"]
