from __future__ import annotations

import threading
import re
import time
import unicodedata
from contextvars import ContextVar
from typing import Optional

# Isolate native inference so a crash or timeout cannot terminate the web server.
_POOL = None
_POOL_LOCK = threading.Lock()
_RUN_LOCK = threading.Lock()
_OCR_TIMEOUT_S = 600

_RAPID = None
settings = ContextVar('ocr_settings', default={})


class OCRProcessingError(RuntimeError):
    pass


def available_engines() -> list[str]:
    """Installed dependencies only. Use probe() to verify actual inference."""
    from importlib.util import find_spec
    try:
        return ['rapidocr'] if all(find_spec(name) is not None for name in ('rapidocr','onnxruntime','numpy')) else []
    except (ImportError, ValueError):
        return []


def configured_engine(config=None):
    selected = (settings.get() if config is None else config).get('engine') or 'auto'
    # Existing settings may still name the removed engine. Upgrade its selection
    # to RapidOCR without importing or installing the old runtime.
    return 'rapidocr' if selected == 'paddleocr' else selected


def ocr_enabled():
    selected = configured_engine()
    return selected != 'none' and (selected != 'auto' or bool(available_engines()))


def normalize_ocr_text(text):
    # Keep line boundaries: never join a number at the end of one OCR block to
    # the next. Offsets are subsequently computed against this same text.
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'(?<=\d)[^\S\r\n]+(?=\d)', '', text)
    date_pattern = r'(?<!\d)(?:19|20)\d{2}[^\S\r\n]*(?:年|[./-])[^\S\r\n]*\d{1,2}[^\S\r\n]*(?:月|[./-])[^\S\r\n]*\d{1,2}(?:[^\S\r\n]*日)?'
    return re.sub(date_pattern, lambda match: re.sub(r'[^\S\r\n]', '', match.group()), text)


def ocr_pixmap(pix) -> tuple[str, list, Optional[str], Optional[str]]:
    # An explicitly disabled engine must not queue behind another document's
    # native OCR request (which may take several minutes or need termination).
    if configured_engine() == 'none':
        return '', [], None, '未启用 OCR，扫描件需人工核对文本'
    if not available_engines():
        return '', [], None, 'RapidOCR 依赖未安装，请安装 requirements-ocr.txt；扫描件需人工核对文本'
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
    selected = configured_engine(cfg)
    selected = (engines[0] if engines else None) if selected == 'auto' else selected
    if selected not in engines:
        return "", [], None, "RapidOCR 依赖未安装，请安装 requirements-ocr.txt；扫描件需人工核对文本"
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
    blocks = [{"text": normalize_ocr_text(t), "raw_text": t, "bbox": b, "conf": c}
              for t, b, c in lines if normalize_ocr_text(t).strip()]
    if not blocks:
        from ai.ocr_status import EMPTY_OCR_WARNING
        return '', [], selected, EMPTY_OCR_WARNING
    return "\n".join(block['text'] for block in blocks), blocks, selected, None


def probe(config=None):
    """Run bundled models on a synthetic Chinese date; never uses uploaded files."""
    started = time.monotonic()
    token = settings.set(dict(settings.get() if config is None else config))
    try:
        import fitz
        from ai.dates import find_dates
        with fitz.open() as document:
            page = document.new_page(width=500,height=180)
            page.insert_text((30,65),'WORKBENCH OCR TEST 2026',fontsize=22)
            page.insert_text((30,115),'虚构学生 申请日期 2026年9月15日',fontname='china-s',fontsize=22)
            dpi = max(72,min(300,int(settings.get().get('min_dpi') or 200)))
            text,blocks,engine,error = ocr_pixmap(page.get_pixmap(dpi=dpi,alpha=False))
        ok = not error and '学生' in text and any(hit.get('date') and hit['date'].isoformat()=='2026-09-15' for hit in find_dates(text))
        return {'ok':bool(ok),'engine':engine,'latency_ms':int((time.monotonic()-started)*1000),
                'message':error or ('RapidOCR 模型加载、中文识别及日期提取通过' if ok else '引擎未正确识别内置中文日期图片'),
                'recognized_text':text,'block_count':len(blocks)}
    except Exception as exc:
        from diagnostics import log_exception
        log_exception('ocr.probe_failed',exc)
        return {'ok':False,'engine':None,'latency_ms':int((time.monotonic()-started)*1000),
                'message':'RapidOCR 自检失败，请检查依赖与模型文件'}
    finally:
        settings.reset(token)


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
                    if process.is_alive():
                        process.kill()
                        process.join(timeout=2)
            _POOL.shutdown(wait=False, cancel_futures=True)
            _POOL = None


def _child_ocr(samples: bytes, width: int, height: int, n: int, selected='rapidocr'):
    import numpy as np
    if selected != 'rapidocr' or n not in (1,3,4) or width <= 0 or height <= 0:
        raise ValueError('invalid OCR input')
    img = np.frombuffer(samples, dtype=np.uint8).reshape(height, width, n)
    if n == 4:
        img = img[:, :, :3]
    if n == 1:
        img = np.repeat(img, 3, axis=2)
    # PyMuPDF supplies RGB; RapidOCR consumes OpenCV BGR arrays.
    img = img[:, :, ::-1].copy()
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
