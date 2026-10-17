from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class IssueDraft:
    category: str
    severity: str
    title: str
    description: str
    rule_code: Optional[str] = None
    rule_basis: Optional[str] = None
    material_id: Optional[int] = None
    material_version_id: Optional[int] = None
    location: dict = field(default_factory=dict)
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    suggestion: Optional[str] = None
    suggestion_example: Optional[str] = None
    needs_human_judgement: bool = False
    confidence: float = 0.9
    source: str = "AI_RULE"
    fingerprint_parts: tuple = ()


def loc(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}
