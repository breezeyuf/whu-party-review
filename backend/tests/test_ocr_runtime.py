import os
import time
from unittest.mock import Mock

import fitz
import pytest

from ai import ocr, parser


def stalled_worker(connection):
    connection.recv()
    time.sleep(60)


def crashed_worker(connection):
    connection.recv()
    os._exit(1)


def echo_worker(connection):
    try:
        while True:
            connection.recv()
            connection.send(([("recovered", [0, 0, 1, 1], 0.99)], None))
    except EOFError:
        pass


@pytest.mark.parametrize("worker,expected", [(stalled_worker, "超时"), (crashed_worker, "异常退出")])
def test_failed_child_is_terminated_and_next_request_recovers(monkeypatch, worker, expected):
    monkeypatch.setattr(ocr, "available_engines", lambda: ["paddleocr"])
    monkeypatch.setattr(ocr, "_OCR_TIMEOUT_S", 1)
    monkeypatch.setattr(ocr, "_serve", worker)
    try:
        lines, error = ocr._call((b"x", 1, 1, 1))
        assert not lines and expected in error
        assert ocr._PROCESS is None and ocr._CONNECTION is None
        monkeypatch.setattr(ocr, "_serve", echo_worker)
        monkeypatch.setattr(ocr, "_OCR_TIMEOUT_S", 10)
        assert ocr._call((b"x", 1, 1, 1))[0][0][0] == "recovered"
    finally:
        ocr.shutdown()


def test_missing_dependencies_cannot_pass_probe(monkeypatch):
    monkeypatch.setattr(ocr, "available_engines", lambda: [])
    result = ocr.probe()
    assert result["ok"] is False and "未安装" in result["message"]


def test_loaded_engine_with_wrong_recognition_cannot_pass_probe(monkeypatch):
    monkeypatch.setattr(ocr, "ocr_pixmap", lambda pix: ("wrong", [], "paddleocr", None))
    assert ocr.probe()["ok"] is False


def test_settings_test_runs_inference(monkeypatch):
    from services.settings import test_ai
    probe = Mock(return_value={"ok": False, "message": "model unavailable"})
    monkeypatch.setattr(ocr, "probe", probe)
    assert test_ai(None, "ocr")["ok"] is False
    probe.assert_called_once()


def test_pixel_boxes_are_converted_to_pdf_points(monkeypatch):
    def recognize(pix):
        return "known", [{"text": "known", "bbox": [0, 0, pix.width, pix.height], "conf": 0.9}], "paddleocr", None
    monkeypatch.setattr(ocr, "ocr_pixmap", recognize)
    with fitz.open() as doc:
        page = doc.new_page(width=300, height=200)
        _, blocks, _, _ = parser._ocr_page(page)
    assert blocks[0]["bbox"] == pytest.approx([0, 0, 300, 200])


@pytest.mark.parametrize("n,samples,expected", [(1, b"\x10", [16, 16, 16]),
    (3, b"\x10\x20\x30", [48, 32, 16]), (4, b"\x10\x20\x30\xff", [48, 32, 16])])
def test_pixmap_is_converted_to_bgr(monkeypatch, n, samples, expected):
    monkeypatch.setattr(ocr, "_child_engine", lambda: object())
    monkeypatch.setattr(ocr, "_ENGINE_V3", True)
    run = Mock(return_value=[])
    monkeypatch.setattr(ocr, "_run_v3", run)
    ocr._child_ocr(samples, 1, 1, n)
    assert run.call_args.args[1][0, 0].tolist() == expected


def test_pdf_classification_tracks_all_page_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(parser, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(parser, "_visual_from_pdf", lambda _: {})
    monkeypatch.setattr(parser, "_ocr_page", lambda _: ("识别正文", [], "paddleocr", None))
    for texts, expected in [([False], "OCR"), ([True, False, False], "MIXED")]:
        path = tmp_path / (expected + ".pdf")
        with fitz.open() as doc:
            for has_text in texts:
                page = doc.new_page()
                if has_text:
                    page.insert_text((30, 40), "This is a long selectable text paragraph.")
            doc.save(path)
        assert parser._parse_pdf(path)["parser"] == expected
