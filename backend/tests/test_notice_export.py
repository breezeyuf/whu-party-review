"""检查实际导出的 PDF 内容、分页与字号，不依赖数据库。"""
from types import SimpleNamespace

import fitz
import pytest

from services.exporter import export_notice_file


def make_notice(*, items=None, completion_items=None, note="", title="材料整改通知"):
    return SimpleNamespace(
        id=1, round_no=2, title=title,
        content={
            "student": {"student_no": "DEMO20260001"},
            "intro": "请根据问题清单补充材料，修改完成后重新提交。",
            "items": items or [], "completion_items": completion_items or [], "note": note,
        },
    )


def problem_items(count):
    return [
        {
            "no": i, "severity": "需修改",
            "problem": f"问题{i:03d}：材料缺少必要的学习与实践经历说明，请对照实际情况补充。",
            "suggestion": f"建议{i:03d}：补充活动时间、具体内容及个人收获，并核对材料中的日期。",
        }
        for i in range(1, count + 1)
    ]


def normalized_text(doc):
    return "".join("".join(page.get_text() for page in doc).split())


def test_short_notice_is_a_readable_single_page_pdf():
    response = export_notice_file(make_notice(items=problem_items(2), note="请核对后提交。"))

    assert response.media_type == "application/pdf"
    assert ".pdf" in response.headers["content-disposition"]
    with fitz.open(stream=response.body, filetype="pdf") as doc:
        assert len(doc) == 1
        text = normalized_text(doc)
        assert "问题001" in text and "建议002" in text
        assert "请核对后提交。" in text


def test_long_notice_paginates_and_preserves_every_issue_at_readable_size():
    response = export_notice_file(make_notice(items=problem_items(45), note="全部问题核对完毕。"))

    with fitz.open(stream=response.body, filetype="pdf") as doc:
        assert len(doc) > 1
        text = normalized_text(doc)
        for i in range(1, 46):
            assert f"问题{i:03d}" in text
            assert f"建议{i:03d}" in text
        assert "全部问题核对完毕。" in text
        for page in doc:
            assert f"{page.number + 1}/{len(doc)}" in "".join(page.get_text().split())
            assert page.rect.width == pytest.approx(595, abs=1)
            assert page.rect.height == pytest.approx(842, abs=1)
            spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block
                     for line in block["lines"] for span in line["spans"] if span["text"].strip()]
            body_spans = [s for s in spans if s["bbox"][1] < page.rect.height - 42]
            assert body_spans
            assert min(s["size"] for s in body_spans) >= 10.5
            for span in body_spans:
                assert span["bbox"][0] >= 35
                assert span["bbox"][2] <= page.rect.width - 35


def test_one_issue_longer_than_a_page_keeps_its_ending():
    item = {"no": 1, "severity": "需修改", "problem": "长段落开始。" + "逐项说明实际情况。" * 400 + "长段落结束。",
            "suggestion": "尾部修改建议。"}
    response = export_notice_file(make_notice(items=[item]))

    with fitz.open(stream=response.body, filetype="pdf") as doc:
        assert len(doc) > 1
        text = normalized_text(doc)
        assert "长段落开始。" in text and "长段落结束。" in text
        assert "尾部修改建议。" in text


def test_long_completion_notice_preserves_all_missing_materials():
    items = [{"material": f"补交材料{i:03d}", "missing": 2} for i in range(1, 61)]
    response = export_notice_file(make_notice(completion_items=items))

    with fitz.open(stream=response.body, filetype="pdf") as doc:
        assert len(doc) > 1
        text = normalized_text(doc)
        for i in range(1, 61):
            assert f"补交材料{i:03d}" in text


def test_notice_fields_with_markup_are_exported_as_literal_text():
    notice = make_notice(
        title="整改通知 <标题> & 核查",
        items=[{"no": 1, "severity": "<需修改>", "problem": "保留 <b>原文</b> & 符号。",
                "suggestion": "请保留 <核对项>。"}],
        completion_items=[{"material": "材料 <附件>", "missing": 1}],
        note="意见 <复核> & 完成。",
    )
    notice.content["intro"] = "说明 <起始> & 核对。"
    response = export_notice_file(notice)

    with fitz.open(stream=response.body, filetype="pdf") as doc:
        text = normalized_text(doc)
        for literal in ("<标题>", "<需修改>", "<b>原文</b>", "<核对项>", "<附件>", "<复核>", "<起始>", "&"):
            assert literal in text
