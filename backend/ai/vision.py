from __future__ import annotations

from typing import Any

import numpy as np


def page_blur(page, dpi: int = 150) -> dict:
    try:
        import cv2
        pix = page.get_pixmap(dpi=dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n >= 3:
            gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)
        else:
            gray = arr[:, :, 0]
        score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        return {"dpi": dpi, "blur_score": score, "is_blurry": score < 60}
    except Exception:
        return {"dpi": dpi, "blur_score": None, "is_blurry": False}


def detect_visual(doc) -> dict:
    seals = []
    signatures = []
    try:
        import cv2
        import fitz
    except Exception:
        return {"seals": [], "signatures": []}
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=120)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        rgb = arr[:, :, :3] if pix.n >= 3 else np.repeat(arr, 3, axis=2)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        mask1 = cv2.inRange(hsv, (0, 40, 40), (10, 255, 255))
        mask2 = cv2.inRange(hsv, (160, 40, 40), (180, 255, 255))
        mask = cv2.bitwise_or(mask1, mask2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sx = page.rect.width / pix.width
        sy = page.rect.height / pix.height
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 80:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            roundness = 0
            peri = cv2.arcLength(cnt, True)
            if peri:
                roundness = 4 * np.pi * area / (peri * peri)
            if roundness > 0.4 and 0.6 < w / max(h, 1) < 1.6:
                conf = min(1.0, roundness)
                seals.append({
                    "page_no": i + 1,
                    "bbox": [x * sx, y * sy, (x + w) * sx, (y + h) * sy],
                    "conf": float(conf),
                })
        text = page.get_text() or ""
        for kw in ("签名", "本人签字", "介绍人", "申请人", "汇报人", "志愿人"):
            if kw in text:
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                # 仅在右下角落款/签名区域内统计墨迹，整页墨迹占比会把正文误判为签名
                x0, y0 = int(pix.width * 0.55), int(pix.height * 0.82)
                x1, y1 = int(pix.width * 0.9), int(pix.height * 0.95)
                region = gray[y0:y1, x0:x1]
                ink = float(np.mean(region < 80)) if region.size else 0.0
                signatures.append({
                    "slot": kw,
                    "page_no": i + 1,
                    "bbox": [page.rect.width * 0.55, page.rect.height * 0.82, page.rect.width * 0.9, page.rect.height * 0.95],
                    "ink_ratio": float(ink),
                    "present": bool(ink > 0.01),
                })
                break
    return {"seals": seals, "signatures": signatures}
