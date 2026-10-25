from __future__ import annotations

from typing import Any

import numpy as np


def page_blur(page, dpi: int | None = None) -> dict:
    from ai.ocr import settings
    cfg = settings.get()
    dpi = dpi or max(72, min(300, int(cfg.get('min_dpi') or 150)))
    threshold = float(cfg.get('blur_threshold', 60))
    try:
        import cv2
        pix = page.get_pixmap(dpi=dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n >= 3:
            gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)
        else:
            gray = arr[:, :, 0]
        score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        # Only substantial embedded scans count; logos must not lower page DPI.
        source_dpis = []
        for info in page.get_image_info():
            x0,y0,x1,y1 = info['bbox']
            if (x1-x0)*(y1-y0) >= page.rect.width*page.rect.height*0.5 and x1>x0 and y1>y0:
                source_dpis.append(min(info['width']*72/(x1-x0), info['height']*72/(y1-y0)))
        return {"dpi": dpi, 'min_dpi':cfg.get('min_dpi',150), 'source_dpi': min(source_dpis) if source_dpis else None,
                "blur_score": score, 'blur_threshold': threshold, "is_blurry": score < threshold}
    except Exception:
        return {"dpi": dpi, "blur_score": None, "is_blurry": False}


def detect_visual(doc, pages=None) -> dict:
    seals = []
    signatures = []
    anchors = []
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
        blocks = next((p.get('blocks', []) for p in (pages or []) if p.get('page_no') == i+1), None)
        if blocks is None:
            blocks = [{'text': b[4], 'bbox': b[:4]} for b in page.get_text('blocks') if len(b)>4 and isinstance(b[4],str)]
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        for block in blocks:
            text, box = block.get('text',''), block.get('bbox')
            if not box or len(box)!=4:
                continue
            keywords = [k for k in ('本人签字','签名','签字','介绍人','申请人','汇报人','谈话人','书记','盖章','印章') if k in text]
            if not keywords:
                continue
            kw = max(keywords,key=len)
            x0,y0,x1,y1 = box
            # Approximate the end of the keyword, including OCR lines that contain a name.
            after = x0+(x1-x0)*(text.index(kw)+len(kw))/max(1,len(text))
            rect = fitz.Rect(after+2,y0,min(page.rect.width,after+145),min(page.rect.height,y1+28)) & page.rect
            if rect.is_empty:
                continue
            entry = {'slot':text[:80], 'page_no':i+1, 'bbox':list(rect), 'anchor_bbox':list(box)}
            anchors.append(entry)
            if kw not in ('盖章','印章'):
                region = gray[max(0,int(rect.y0/sy)):int(rect.y1/sy),max(0,int(rect.x0/sx)):int(rect.x1/sx)]
                ink = float(np.mean(region < 80)) if region.size else 0.0
                signatures.append({**entry,'ink_ratio':ink,'present':ink>0.01,'conf':0.6,'method':'keyword_ink'})
    return {"seals": seals, "signatures": signatures, 'anchors':anchors}
