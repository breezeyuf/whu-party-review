from __future__ import annotations

import os
import threading
import time
from typing import Optional
from diagnostics import log_exception

# The child owns native model code. A timed-out child is terminated before retry.
_LOCK = threading.Lock()
_PROCESS = None
_CONNECTION = None
_OCR_TIMEOUT_S = max(1, int(os.getenv("OCR_TIMEOUT_S", "180")))
_ENGINE = None
_ENGINE_V3 = False


class OCRProcessingError(RuntimeError):
    pass


def available_engines() -> list[str]:
    """Installed dependencies only; not model readiness."""
    from importlib.util import find_spec
    try:
        return ["paddleocr"] if all(find_spec(n) is not None for n in ("paddleocr", "paddle", "numpy")) else []
    except (ImportError, ValueError):
        return []


def ocr_pixmap(pix) -> tuple[str, list, Optional[str], Optional[str]]:
    lines, error = _call((bytes(pix.samples), pix.width, pix.height, pix.n))
    if error:
        return "", [], None, error
    blocks = [{"text": t, "bbox": b, "conf": c} for t, b, c in lines]
    return "\n".join(t for t, _, _ in lines), blocks, "paddleocr", None


def probe() -> dict:
    started = time.monotonic()
    try:
        import fitz
        with fitz.open() as document:
            page = document.new_page(width=400, height=100)
            page.insert_text((20, 60), "OCR 12345", fontsize=32)
            text, blocks, engine, error = ocr_pixmap(page.get_pixmap(dpi=150, alpha=False))
        ok = error is None and "12345" in "".join(text.split())
        message = error or ("模型加载及测试图片识别成功" if ok else "模型已运行，但未正确识别测试图片")
        return {"ok": ok, "engine": engine, "latency_ms": int((time.monotonic() - started) * 1000),
                "message": message, "recognized_text": text, "block_count": len(blocks)}
    except Exception as exc:
        log_exception("ocr.probe_failed", exc)
        return {"ok": False, "engine": None, "latency_ms": int((time.monotonic() - started) * 1000),
                "message": "OCR 自检失败，请检查依赖与模型配置"}


def _call(payload):
    if not available_engines():
        return [], "OCR 依赖未安装，请按 OCR 部署说明安装引擎"
    if not _LOCK.acquire(timeout=_OCR_TIMEOUT_S):
        return [], "OCR 繁忙，请稍后重试"
    try:
        _, connection = _worker()
        connection.send(payload)
        if not connection.poll(_OCR_TIMEOUT_S):
            _stop_locked()
            return [], "OCR 识别超时，进程已重置，可重试"
        return connection.recv()
    except (EOFError, BrokenPipeError, OSError) as exc:
        log_exception("ocr.worker_failed", exc)
        _stop_locked()
        return [], "OCR 进程异常退出，已重置，可重试"
    except Exception as exc:
        log_exception("ocr.request_failed", exc)
        _stop_locked()
        return [], "OCR 调用失败，请检查模型配置后重试"
    finally:
        _LOCK.release()


def _worker():
    global _PROCESS, _CONNECTION
    if _PROCESS is None or not _PROCESS.is_alive():
        _stop_locked()
        import multiprocessing as mp
        context = mp.get_context("spawn")
        parent, child = context.Pipe()
        process = context.Process(target=_serve, args=(child,), daemon=True)
        try:
            process.start()
        except BaseException:
            parent.close()
            child.close()
            raise
        child.close()
        _PROCESS, _CONNECTION = process, parent
    return _PROCESS, _CONNECTION


def _stop_locked():
    global _PROCESS, _CONNECTION
    process, connection = _PROCESS, _CONNECTION
    _PROCESS = _CONNECTION = None
    if connection is not None:
        connection.close()
    if process is not None:
        if process.is_alive():
            process.terminate()
        process.join(timeout=3)
        if process.is_alive():
            process.kill()
            process.join(timeout=3)
        if not process.is_alive():
            process.close()


def shutdown():
    with _LOCK:
        _stop_locked()


def _serve(connection):
    try:
        while True:
            payload = connection.recv()
            try:
                result = _child_ocr(*payload)
            except OCRProcessingError as exc:
                result = ([], str(exc))
            except Exception as exc:
                log_exception("ocr.inference_failed", exc)
                result = ([], "OCR 模型加载或识别失败，请检查模型文件与运行依赖")
            connection.send(result)
    except (EOFError, BrokenPipeError):
        pass
    finally:
        connection.close()


def _child_ocr(samples, width, height, n):
    import numpy as np
    if n not in (1, 3, 4) or width <= 0 or height <= 0:
        raise ValueError("invalid OCR image")
    image = np.frombuffer(samples, dtype=np.uint8).reshape(height, width, n)
    # PyMuPDF is RGB(A); Paddle ndarray input is BGR.
    image = np.repeat(image, 3, axis=2) if n == 1 else image[:, :, :3][:, :, ::-1].copy()
    engine = _child_engine()
    return (_run_v3(engine, image) if _ENGINE_V3 else _run_v2(engine, image)), None


def _child_engine():
    global _ENGINE, _ENGINE_V3
    if _ENGINE is not None:
        return _ENGINE
    from importlib.metadata import version
    from pathlib import Path
    cache = os.getenv("OCR_MODEL_CACHE_DIR") or os.getenv("PADDLE_PDX_CACHE_HOME")
    if cache:
        if os.name == "nt" and not str(Path(cache).resolve()).isascii():
            raise OCRProcessingError("Windows OCR 模型缓存需使用英文路径，请设置 OCR_MODEL_CACHE_DIR")
        os.environ["PADDLE_PDX_CACHE_HOME"] = str(Path(cache).resolve())
    from paddleocr import PaddleOCR
    _ENGINE_V3 = int(version("paddleocr").split(".")[0]) >= 3
    if _ENGINE_V3:
        options = dict(device="cpu", use_doc_orientation_classify=False,
                       use_doc_unwarping=False, use_textline_orientation=False,
                       enable_mkldnn=False, cpu_threads=2,
                       text_detection_model_name="PP-OCRv5_mobile_det",
                       text_recognition_model_name="PP-OCRv5_mobile_rec")
        for setting, option in (("OCR_DET_MODEL_DIR", "text_detection_model_dir"),
                                ("OCR_REC_MODEL_DIR", "text_recognition_model_dir")):
            if os.getenv(setting):
                directory = Path(os.environ[setting]).resolve()
                if not directory.is_dir() or (os.name == "nt" and not str(directory).isascii()):
                    raise OCRProcessingError("OCR 本地模型目录不存在或包含非英文路径，请检查模型配置")
                options[option] = str(directory)
        _ENGINE = PaddleOCR(**options)
    else:
        _ENGINE = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False, use_gpu=False)
    return _ENGINE


def _run_v3(engine, image):
    out = []
    for result in engine.predict(image) or []:
        boxes = result.get("rec_boxes")
        for i, text in enumerate(result.get("rec_texts") or []):
            box = [float(v) for v in boxes[i]] if boxes is not None and len(boxes) > i else []
            out.append((text, box, float(result["rec_scores"][i])))
    return out


def _run_v2(engine, image):
    out = []
    result = engine.ocr(image)
    if result and result[0]:
        for line in result[0]:
            box, (text, confidence) = line[0], line[1]
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            out.append((text, [min(xs), min(ys), max(xs), max(ys)], float(confidence)))
    return out
