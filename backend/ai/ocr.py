from __future__ import annotations

import threading
from typing import Optional

# PaddleOCR runs in a dedicated spawned child process: inside the uvicorn process its native
# runtime terminated the whole server (exit code 1, no Python traceback) during model init.
_POOL = None
_POOL_LOCK = threading.Lock()
_OCR_TIMEOUT_S = 600

_ENGINE = None  # child-process only
_ENGINE_V3 = False


def available_engines() -> list[str]:
    # find_spec avoids importing paddle (~12s), which made /api/health time out
    from importlib.util import find_spec
    out = []
    try:
        if find_spec("paddleocr") is not None:
            out.append("paddleocr")
    except Exception:
        pass
    return out


def ocr_pixmap(pix) -> tuple[str, list, Optional[str], Optional[str]]:
    if not available_engines():
        return "", [], None, "未启用 OCR，扫描件需人工核对文本"
    from concurrent.futures.process import BrokenProcessPool
    try:
        fut = _pool().submit(_child_ocr, bytes(pix.samples), pix.width, pix.height, pix.n)
        lines, err = fut.result(timeout=_OCR_TIMEOUT_S)
    except BrokenProcessPool:
        _reset_pool()
        return "", [], None, "OCR 进程异常退出，扫描件需人工核对文本"
    except Exception as e:
        return "", [], None, f"OCR 失败：{e}"
    if err:
        return "", [], None, err
    blocks = [{"text": t, "bbox": b, "conf": c} for t, b, c in lines]
    return "\n".join(t for t, _, _ in lines), blocks, "paddleocr", None


def shutdown() -> None:
    _reset_pool()


def _pool():
    global _POOL
    with _POOL_LOCK:
        if _POOL is None:
            import multiprocessing as mp
            from concurrent.futures import ProcessPoolExecutor
            _POOL = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn"))
        return _POOL


def _reset_pool() -> None:
    global _POOL
    with _POOL_LOCK:
        if _POOL is not None:
            _POOL.shutdown(wait=False, cancel_futures=True)
            _POOL = None


def _child_ocr(samples: bytes, width: int, height: int, n: int):
    import numpy as np
    engine = _child_engine()
    if engine is None:
        return [], "未启用 OCR，扫描件需人工核对文本"
    img = np.frombuffer(samples, dtype=np.uint8).reshape(height, width, n)
    if n == 4:
        img = img[:, :, :3]
    try:
        return (_run_v3(engine, img) if _ENGINE_V3 else _run_v2(engine, img)), None
    except Exception as e:
        return [], f"OCR 失败：{e}"


def _child_engine():
    global _ENGINE, _ENGINE_V3
    if _ENGINE is not None:
        return _ENGINE
    try:
        from paddleocr import PaddleOCR
        try:
            # PaddleOCR 3.x; oneDNN breaks on the PIR executor in paddlepaddle 3.3
            _ENGINE = PaddleOCR(lang="ch", use_doc_orientation_classify=False, use_doc_unwarping=False,
                                use_textline_orientation=True, enable_mkldnn=False)
            _ENGINE_V3 = True
        except (TypeError, ValueError):
            _ENGINE = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
            _ENGINE_V3 = False
    except Exception as e:
        print("[ocr] engine unavailable:", e, flush=True)
        _ENGINE = None
    return _ENGINE


def _run_v3(engine, img) -> list:
    out = []
    for r in engine.predict(img) or []:
        boxes = r.get("rec_boxes")
        for i, txt in enumerate(r.get("rec_texts") or []):
            box = [float(v) for v in boxes[i]] if boxes is not None and len(boxes) > i else []
            out.append((txt, box, float(r["rec_scores"][i])))
    return out


def _run_v2(engine, img) -> list:
    out = []
    result = engine.ocr(img)
    if result and result[0]:
        for line in result[0]:
            box, (txt, conf) = line[0], line[1]
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            out.append((txt, [min(xs), min(ys), max(xs), max(ys)], float(conf)))
    return out
