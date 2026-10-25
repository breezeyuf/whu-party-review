"""One interpretation of corrected evidence, including deliberate empty corrections."""
import re


def effective_text(parsed):
    if parsed is None:
        return ''
    corrected = getattr(parsed, 'corrected_text', None)
    return corrected if corrected is not None else (parsed.full_text or '')


def effective_fields(parsed):
    if parsed is None:
        return {}
    corrected = getattr(parsed, 'corrected_fields', None)
    if corrected is not None:
        return corrected
    if getattr(parsed, 'corrected_text', None) is not None:
        from ai.extract import extract_fields
        return extract_fields(effective_text(parsed))
    return getattr(parsed, 'extracted_fields', None) or {}


def char_count(text):
    return len(re.sub(r'\s+', '', text or ''))
