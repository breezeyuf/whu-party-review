"""Measured layout properties: unknown values are not presumed compliant."""
import math


def _measurement(value, *, allow_zero=False):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and (number >= 0 if allow_zero else number > 0) else None


def _styles(style):
    seen = set()
    while style is not None and style.style_id not in seen:
        seen.add(style.style_id)
        yield style
        style = style.base_style


def docx_features(doc):
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    def paragraphs(container):
        for block in container.iter_inner_content():
            if isinstance(block, Paragraph):
                yield block
            elif isinstance(block, Table):
                for row in block.rows:
                    for cell in row.cells:
                        yield from paragraphs(cell)
    samples = []
    for p in paragraphs(doc):
        if not p.text.strip():
            continue
        styles = list(_styles(p.style))
        spacing = next((s.paragraph_format.line_spacing for s in [p, *styles]
                        if s.paragraph_format.line_spacing is not None), None)
        unit = 'pt' if hasattr(spacing, 'pt') else 'multiple'
        for r in p.runs:
            if not r.text.strip():
                continue
            fonts = [r.font, *[s.font for s in _styles(r.style)], *[s.font for s in styles]]
            name = None
            for font in fonts:
                rpr = font._element.rPr
                east = rpr.rFonts.get(qn('w:eastAsia')) if rpr is not None and rpr.rFonts is not None else None
                if east or font.name:
                    name = east or font.name
                    break
            size = next((f.size.pt for f in fonts if f.size is not None), None)
            samples.append({'font': name, 'size_pt': size, 'line_spacing': spacing.pt if unit == 'pt' else spacing,
                            'line_spacing_unit': unit})
    sections = [{'orientation': 'landscape' if s.page_width > s.page_height else 'portrait',
                 'margins_cm': {side: round(getattr(s, side + '_margin').cm, 3)
                                if getattr(s, side + '_margin') is not None else None
                                for side in ('left', 'right', 'top', 'bottom')}} for s in doc.sections]
    return {**(samples[0] if samples else {}), 'samples': samples, 'sections': sections, 'converted_from': 'docx'}


def check_layout(features, layout):
    allowed = {'font','size_pt','line_spacing','line_spacing_unit','margin_cm'}
    if not isinstance(features, dict) or not isinstance(layout, dict) or set(layout) - allowed:
        return [],False
    if not set(layout).intersection(allowed - {'line_spacing_unit'}):
        return [],False
    if 'font' in layout and (not isinstance(layout['font'], str) or not layout['font'].strip()):
        return [],False
    if layout.get('line_spacing_unit', 'multiple') not in ('multiple', 'pt'):
        return [],False
    expected = {key: _measurement(layout[key], allow_zero=key == 'margin_cm')
                for key in ('size_pt','line_spacing','margin_cm') if key in layout}
    if any(value is None for value in expected.values()):
        return [],False
    problems, complete = [], True
    for key in ('font', 'size_pt', 'line_spacing'):
        if key not in layout:
            continue
        for sample in features.get('samples') or [features]:
            actual = sample.get(key)
            measured = actual if key == 'font' else _measurement(actual)
            if measured is None:
                complete = False
            elif key == 'line_spacing' and sample.get('line_spacing_unit', 'multiple') != layout.get('line_spacing_unit', 'multiple'):
                problems.append('行距单位不一致')
            elif (str(actual) != str(layout[key]) if key == 'font' else abs(measured-expected[key]) > 0.05):
                problems.append(f'{key}: {actual}（要求 {layout[key]}）')
    if 'margin_cm' in layout:
        sections = features.get('sections') or []
        if not sections:
            complete = False
        for section in sections:
            for side in ('left','right','top','bottom'):
                actual = (section.get('margins_cm') or {}).get(side)
                measured = _measurement(actual, allow_zero=True)
                if measured is None:
                    complete = False
                elif abs(measured-expected['margin_cm']) > 0.05:
                    problems.append(f'{side} 页边距 {actual} cm（要求 {layout["margin_cm"]}）')
    return list(dict.fromkeys(problems)), complete
