"""Extract explicitly connected date ranges without ordering unrelated dates."""
import re
from datetime import date

from ai.dates import FULLWIDTH, find_dates
from ai.date_evidence import REVIEW_PREFIX


CONNECTOR = r'(?:至|到|[-—–~～]{1,2})'
START_LABEL = r'(?:开始|起始|培训起|公示起)(?:日期|时间)?\s*[:：]?\s*$'
END_LABEL = r'[\s,，;；]*?(?:结束|截止|培训止|公示止)(?:日期|时间)?\s*[:：]?\s*'
SHORT_END = re.compile(r'\s*' + CONNECTOR + r'\s*(?:(?P<month>\d{1,2})\s*月\s*)?(?P<day>\d{1,2})\s*日')


def _context(text, start, end):
    before = text[max(0, start - 100):start]
    lines = before.splitlines()
    prefix = before.rsplit('\n', 1)[-1]
    # A standalone heading can label a range on the next line. Do not carry
    # a previous row's dates across to a different field.
    if not prefix.strip() and lines and not find_dates(lines[-1]):
        prefix = lines[-1]
    suffix = text[end:end + 25].split('\n', 1)[0]
    return prefix + suffix


def explicit_ranges(text, dates, keywords, *, typed=False):
    """Return source spans; multiple possible periods remain separate candidates."""
    normalized = text.translate(FULLWIDTH)
    candidates = []
    for index, start in enumerate(dates):
        finish = dates[index + 1] if index + 1 < len(dates) else None
        gap = normalized[start['end']:finish['start']] if finish else None
        prefix = normalized[max(0, start['start'] - 30):start['start']]
        joined = gap is not None and (
            re.fullmatch(r'\s*' + CONNECTOR + r'\s*', gap)
            or (re.search(START_LABEL, prefix) and re.fullmatch(END_LABEL, gap)))
        short = None if joined else SHORT_END.match(normalized, start['end'])
        if joined:
            end_date, end_pos, error = finish['date'], finish['end'], finish.get('invalid_reason')
        elif short and start['date']:
            try:
                end_date = date(start['date'].year, int(short['month'] or start['date'].month), int(short['day']))
                error = None
            except ValueError:
                end_date, error = None, '结束日期非法'
            end_pos = short.end()
        else:
            continue
        error = start.get('invalid_reason') or error
        if start['date'] and end_date and end_date < start['date']:
            error = '结束日期早于开始日期'
            if short:
                error = REVIEW_PREFIX + '结束日期省略年份且早于开始日期，须核对是否跨年'
        candidates.append({**start, 'end': end_pos, 'end_date': end_date,
                           'raw': text[start['start']:end_pos].strip(), 'invalid_reason': error})

    def relevant(hit):
        context = _context(normalized, hit['start'], hit['end'])
        return any((re.search(r'学时(?!间)', context) if keyword == '学时' else keyword in context)
                   for keyword in keywords)

    selected = [hit for hit in candidates if relevant(hit)]
    if not selected and typed:
        # A material type alone does not prove that an unrelated labelled
        # interval (for example a certificate's validity) is the training period.
        selected = candidates
        for hit in selected:
            context = _context(normalized, hit['start'], hit['end']).strip(' :：,，;；。')
            if context and context not in ('时间', '日期', '起止时间', '起止日期'):
                hit['invalid_reason'] = REVIEW_PREFIX + '区间缺少对应节点的明确标签，须核对用途'
    unique = {}
    for hit in selected:
        key = (hit['date'], hit['end_date'], hit.get('invalid_reason'))
        unique.setdefault(key, hit)
    selected = list(unique.values())
    if len(selected) > 1:
        for hit in selected:
            hit['invalid_reason'] = REVIEW_PREFIX + '发现多组日期区间，须确认本材料适用的起止日期'
    if selected:
        return selected

    singles = [hit for hit in dates if relevant(hit)]
    if not singles and typed:
        singles = dates
    if singles:
        return [{**hit, 'end_date': None, 'invalid_reason': REVIEW_PREFIX + '未找到明确起止关系，须确认完整日期区间'}
                for hit in singles]
    if typed:
        return [{'date': None, 'end_date': None, 'raw': None, 'invalid_reason': '未识别到明确日期区间'}]
    return []
