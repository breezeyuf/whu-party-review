from __future__ import annotations

import threading
from contextvars import ContextVar
from typing import Optional

# PaddleOCR runs in a dedicated spawned child process: inside the uvicorn process its native
# runtime terminated the whole server (exit code 1, no Python traceback) during model init.
_POOL = None
_POOL_LOCK = threading.Lock()
_RUN_LOCK = threading.Lock()
_OCR_TIMEOUT_S = 600

_ENGINE = None  # child-process only
_ENGINE_V3 = False
_RAPID = None
settings = ContextVar('ocr_settings', default={})


class OCRProcessingError(RuntimeError):
    pass


def available_engines() -> list[str]:
    # find_spec avoids importing paddle (~12s), which made /api/health time out
    from importlib.util import find_spec
    out = []
    if find_spec('rapidocr') is not None and find_spec('onnxruntime') is not None:
        out.append('rapidocr')
    try:
        if find_spec("paddleocr") is not None:
            out.append("paddleocr")
    except Exception:
        pass
    return out


def ocr_pixmap(pix) -> tuple[str, list, Optional[str], Optional[str]]:
    # An explicitly disabled engine must not queue behind another document's
    # native OCR request (which may take several minutes or need termination).
    if settings.get().get('engine') == 'none':
        return '', [], None, '未启用 OCR，扫描件需人工核对文本'
    timeout = max(1, float(settings.get().get('timeout_s') or _OCR_TIMEOUT_S))
    if not _RUN_LOCK.acquire(timeout=timeout):
        return '', [], None, 'OCR 排队超时，请重试'
    try:
        return _ocr_pixmap(pix)
    finally:
        _RUN_LOCK.release()


def _ocr_pixmap(pix):
    cfg = settings.get()
    engines = available_engines()
    selected = cfg.get('engine', 'auto')
    selected = (engines[0] if engines else None) if selected == 'auto' else selected
    if selected not in engines:
        return "", [], None, "未启用 OCR，扫描件需人工核对文本"
    from concurrent.futures.process import BrokenProcessPool
    try:
        fut = _pool().submit(_child_ocr, bytes(pix.samples), pix.width, pix.height, pix.n, selected)
        lines, err = fut.result(timeout=max(1, float(cfg.get('timeout_s') or _OCR_TIMEOUT_S)))
    except TimeoutError:
        _reset_pool()
        return '', [], None, 'OCR 超时，请重试或人工核对文本'
    except BrokenProcessPool:
        _reset_pool()
        return "", [], None, "OCR 进程异常退出，扫描件需人工核对文本"
    except Exception:
        return "", [], None, "OCR 引擎执行失败，请检查模型后重试"
    if err:
        # Child errors can contain material text, local paths, or native runtime
        # details. Only a fixed message may become persisted parse diagnostics.
        return "", [], None, 'OCR 引擎识别失败，请检查模型后重试'
    blocks = [{"text": t, "bbox": b, "conf": c} for t, b, c in lines]
    return "\n".join(t for t, _, _ in lines), blocks, selected, None


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
            for process in list((_POOL._processes or {}).values()):
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
            _POOL.shutdown(wait=False, cancel_futures=True)
            _POOL = None


def _child_ocr(samples: bytes, width: int, height: int, n: int, selected='paddleocr'):
    import numpy as np
    img = np.frombuffer(samples, dtype=np.uint8).reshape(height, width, n)
    if n == 4:
        img = img[:, :, :3]
    if n == 1:
        img = np.repeat(img, 3, axis=2)
    # PyMuPDF supplies RGB, both OCR engines consume OpenCV BGR arrays.
    img = img[:, :, ::-1].copy()
    if selected == 'rapidocr':
        global _RAPID
        from rapidocr import RapidOCR
        if _RAPID is None:
            _RAPID = RapidOCR()
        result = _RAPID(img)
        lines = []
        if result.txts is not None:
            for txt, box, score in zip(result.txts, result.boxes, result.scores):
                xs, ys = box[:, 0], box[:, 1]
                lines.append((txt, [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))], float(score)))
        return lines, None
    engine = _child_engine()
    if engine is None:
        return [], "未启用 OCR，扫描件需人工核对文本"
    try:
        return (_run_v3(engine, img) if _ENGINE_V3 else _run_v2(engine, img)), None
    except Exception:
        return [], 'OCR 引擎识别失败，请检查模型后重试'


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
