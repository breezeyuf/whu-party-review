from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models import Archive


def desensitize_text(text: str, archive: Optional[Archive] = None) -> str:
    if not text:
        return text
    s = text
    if archive:
        if archive.real_name:
            s = s.replace(archive.real_name, "[姓名]")
        if archive.student_no:
            s = s.replace(archive.student_no, "[学号]")
    s = re.sub(r"(?<!\d)1[3-9]\d{9}(?!\d)", "[手机号]", s)
    s = re.sub(r"(?<!\d)\d{17}[\dXx](?!\d)", "[身份证号]", s)
    return s
