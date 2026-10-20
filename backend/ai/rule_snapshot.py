"""Detached, immutable rule inputs for one formal review.

Rule tables come exclusively from RuleVersion.snapshot. Calendar and date are
captured separately at review start because settings do not publish rule versions.
No credentials or provider configuration belong in the persisted context.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from collections.abc import Mapping

from utils import now


RULE_GROUPS = (
    "material_types", "checklist_items", "time_node_defs", "time_rules",
    "check_rules", "political_terms", "sensitive_phrases",
    "suggestion_templates", "prompt_templates",
)


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _plain(value):
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class RuleRow:
    values: Mapping

    def __getattr__(self, name):
        try:
            return self.values[name]
        except KeyError:
            raise AttributeError(name) from None


@dataclass(frozen=True)
class RuleSet:
    version_id: int
    version_no: int
    digest: str
    groups: Mapping

    @classmethod
    def from_version(cls, version):
        snapshot = version.snapshot
        if not isinstance(snapshot, dict) or any(
            not isinstance(snapshot.get(key), list)
            or any(not isinstance(row, dict) for row in snapshot[key])
            for key in RULE_GROUPS
        ):
            # A corrupt/partial version must never silently consult live rules.
            raise ValueError("规则快照不完整，无法执行审核")
        encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False)
        detached = json.loads(encoded)
        groups = MappingProxyType({key: tuple(RuleRow(_freeze(row)) for row in detached[key])
                                   for key in RULE_GROUPS})
        result = cls(version.id, version.version_no,
                     hashlib.sha256(encoded.encode("utf-8")).hexdigest(), groups)
        type_ids = {row.id for row in result.rows("material_types", active=False)}
        if any(row.material_type_id not in type_ids for row in result.rows("checklist_items")):
            raise ValueError("规则快照的清单引用了不存在的材料类型")
        return result

    def rows(self, group, *, active=True):
        rows = self.groups[group]
        return tuple(sorted((row for row in rows if not active or row.is_active),
                            key=lambda row: (row.values.get("sort_order") or 0, row.id)))

    @property
    def types(self):
        return {row.id: row for row in self.rows("material_types", active=False)}


@dataclass(frozen=True)
class EvaluationContext:
    rule_version_id: int
    snapshot_sha256: str
    checked_at: str
    today: date
    batch_end: date | None
    calendar: Mapping
    classify_confidence_threshold: float

    @classmethod
    def capture(cls, rules, calendar, batch_end, classify_confidence_threshold=0.7):
        stamp = now()
        return cls(rules.version_id, rules.digest, stamp.isoformat(), stamp.date(), batch_end,
                   _freeze(json.loads(json.dumps(calendar))), float(classify_confidence_threshold))

    def validate(self, rules):
        if (self.rule_version_id, self.snapshot_sha256) != (rules.version_id, rules.digest):
            raise ValueError("检查上下文与规则快照不匹配")

    def to_dict(self):
        return {
            "format_version": 1,
            "rule_version_id": self.rule_version_id,
            "snapshot_sha256": self.snapshot_sha256,
            "checked_at": self.checked_at,
            "today": self.today.isoformat(),
            "batch_end": self.batch_end.isoformat() if self.batch_end else None,
            "calendar": _plain(self.calendar),
            "calendar_source": "CHECK_START_SETTINGS",
            "classify_confidence_threshold": self.classify_confidence_threshold,
            # Preserve the existing R-T21 semantics, rather than silently redefining it.
            "upload_date_policy": "CHECK_DATE",
        }
