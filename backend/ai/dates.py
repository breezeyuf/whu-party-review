from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta

CN_DIGITS = {
    "〇": 0, "零": 0, "○": 0, "Ｏ": 0, "0": 0,
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "壹": 1, "贰": 2, "叁": 3, "肆": 4, "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9, "拾": 10,
    "两": 2, "〇": 0,
}
CN_YEAR = str.maketrans({
    "〇": "0", "零": "0", "○": "0", "Ｏ": "0",
    "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
    "六": "6", "七": "7", "八": "8", "九": "9",
    "壹": "1", "贰": "2", "叁": "3", "肆": "4", "伍": "5",
    "陆": "6", "柒": "7", "捌": "8", "玖": "9",
})

# OCR often emits full-width digits/separators; 1:1 mapping keeps match offsets valid for the original text
FULLWIDTH = str.maketrans({**{chr(0xFF10 + i): str(i) for i in range(10)}, "．": ".", "／": "/", "－": "-"})

DATE_PATTERNS = [
    re.compile(r"(?P<y>20\d{2}|19\d{2})\s*[年\./\-]\s*(?P<m>\d{1,2})\s*[月\./\-]\s*(?P<d>\d{1,2})\s*日?"),
    re.compile(r"(?P<y>20\d{2}|19\d{2})(?P<m>0[1-9]|1[0-2])(?P<d>0[1-9]|[12]\d|3[01])"),
]


def _cn_month_day(text: str) -> Optional[int]:
    text = text.strip()
    if text.isdigit():
        return int(text)
    if text == "十":
        return 10
    if text.startswith("十"):
        rest = text[1:]
        return 10 + (CN_DIGITS.get(rest, 0) if rest else 0)
    if "十" in text:
        a, b = text.split("十", 1)
        return CN_DIGITS.get(a, 0) * 10 + (CN_DIGITS.get(b, 0) if b else 0)
    if len(text) == 1 and text in CN_DIGITS:
        return CN_DIGITS[text]
    return None


def parse_date(text: Optional[str]) -> tuple[Optional[date], Optional[str], Optional[str]]:
    if not text:
        return None, None, "空日期"
    raw = str(text).strip()
    s = raw.translate(FULLWIDTH).replace(" ", "")
    for pat in DATE_PATTERNS:
        m = pat.search(s)
        if m:
            try:
                d = date(int(m.group("y")), int(m.group("m")), int(m.group("d")))
                return d, m.group(0), None
            except ValueError:
                return None, m.group(0), "非法日期"
    m = re.search(r"([〇零○Ｏ一二三四五六七八九0-9]{4})年([十〇零一二三四五六七八九十]+)月([十〇零一二三四五六七八九十]+)日", s)
    if m:
        try:
            y = int(m.group(1).translate(CN_YEAR))
            mo = _cn_month_day(m.group(2))
            d = _cn_month_day(m.group(3))
            if mo and d:
                return date(y, mo, d), m.group(0), None
        except ValueError:
            return None, m.group(0), "非法日期"
        return None, m.group(0), "日期不完整"
    m = re.search(r"(20\d{2}|19\d{2})年(\d{1,2})月", s)
    if m:
        return None, m.group(0), "日期缺日"
    return None, None, "未识别到日期"


def find_dates(text: str) -> list[dict]:
    if not text:
        return []
    text = text.translate(FULLWIDTH)
    found = []
    seen = set()
    for pat in DATE_PATTERNS:
        for m in pat.finditer(text):
            span = (m.start(), m.end())
            if span in seen:
                continue
            seen.add(span)
            d, raw, err = parse_date(m.group(0))
            found.append({"date": d, "raw": raw or m.group(0), "start": m.start(), "end": m.end(), "invalid_reason": err})
    for m in re.finditer(r"[〇零○Ｏ一二三四五六七八九]{4}年[十〇零一二三四五六七八九十]+月[十〇零一二三四五六七八九十]+日", text):
        span = (m.start(), m.end())
        if span in seen:
            continue
        seen.add(span)
        d, raw, err = parse_date(m.group(0))
        found.append({"date": d, "raw": raw or m.group(0), "start": m.start(), "end": m.end(), "invalid_reason": err})
    found.sort(key=lambda x: x["start"])
    return found


def add_duration(d: date, value: int, unit: str) -> date:
    unit = (unit or "DAY").upper()
    if unit == "DAY":
        return d + timedelta(days=value)
    if unit == "MONTH":
        return d + relativedelta(months=value)
    if unit == "YEAR":
        return d + relativedelta(years=value)
    if unit == "WORKDAY":
        return add_workdays(d, value, set(), set())
    return d + timedelta(days=value)


def diff_days(a: date, b: date) -> int:
    return (b - a).days


def age_years(birth: date, at: date) -> int:
    years = at.year - birth.year
    if (at.month, at.day) < (birth.month, birth.day):
        years -= 1
    return years


def add_workdays(start: date, n: int, holidays: set[date], extra: set[date]) -> date:
    cur = start
    added = 0
    step = 1 if n >= 0 else -1
    target = abs(n)
    while added < target:
        cur = cur + timedelta(days=step)
        if is_workday(cur, holidays, extra):
            added += 1
    return cur


def workdays_between(a: date, b: date, holidays: set[date], extra: set[date]) -> int:
    if b < a:
        return -workdays_between(b, a, holidays, extra)
    n = 0
    cur = a
    while cur < b:
        cur = cur + timedelta(days=1)
        if is_workday(cur, holidays, extra):
            n += 1
    return n


def is_workday(d: date, holidays: set[date], extra: set[date]) -> bool:
    if d in extra:
        return True
    if d in holidays:
        return False
    return d.weekday() < 5


def duration_meets(a: date, b: date, min_value: int, unit: str, holidays=None, extra=None) -> bool:
    unit = (unit or "DAY").upper()
    holidays = holidays or set()
    extra = extra or set()
    if unit == "WORKDAY":
        return workdays_between(a, b, holidays, extra) >= min_value
    if unit == "DAY":
        return (b - a).days >= min_value
    if unit == "MONTH":
        return a + relativedelta(months=min_value) <= b
    if unit == "YEAR":
        return a + relativedelta(years=min_value) <= b
    return (b - a).days >= min_value


def describe_interval(a: date, b: date) -> str:
    if b < a:
        return describe_interval(b, a) + "（顺序颠倒）"
    rd = relativedelta(b, a)
    parts = []
    if rd.years:
        parts.append(f"{rd.years} 年")
    if rd.months:
        parts.append(f"{rd.months} 个月")
    if rd.days or not parts:
        parts.append(f"{rd.days} 天")
    return "".join(parts) if len(parts) == 1 else " ".join(parts)
