from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, date, time, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from errors import unprocessable
from models import AiReport, Archive, Issue, Material, MaterialType, ReviewRecord, Submission
from services.scope import scoped_archives, scoped_submissions
from utils import TZ8


FILTER_KEYS = ("batch_id", "college_id", "branch_id", "stage_code", "date_from", "date_to")


def normalize_filters(filters: dict) -> dict:
    """Validate once at the API boundary and again when a queued export runs."""
    out = {}
    for key in FILTER_KEYS:
        value = filters.get(key)
        if value in (None, ""):
            continue
        try:
            if key.startswith("date_"):
                value = date.fromisoformat(str(value))
            else:
                if isinstance(value, bool) or str(value) != str(int(value)):
                    raise ValueError()
                value = int(value)
                if value < 1 or (key == "stage_code" and value not in range(1, 6)):
                    raise ValueError()
        except (ValueError, TypeError):
            raise unprocessable(f"筛选条件 {key} 格式无效")
        out[key] = value
    if out.get("date_from") and out.get("date_to") and out["date_from"] > out["date_to"]:
        raise unprocessable("开始日期不得晚于结束日期")
    return out


def apply_filters(q, model, batch_id=None, college_id=None, branch_id=None, stage_code=None, date_from=None, date_to=None):
    values = normalize_filters(dict(batch_id=batch_id, college_id=college_id, branch_id=branch_id,
                                   stage_code=stage_code, date_from=date_from, date_to=date_to))
    if batch_id:
        q = q.filter(model.batch_id == int(batch_id))
    if college_id and hasattr(model, "college_id"):
        q = q.filter(model.college_id == int(college_id))
    if branch_id and hasattr(model, "branch_id"):
        q = q.filter(model.branch_id == int(branch_id))
    if stage_code and hasattr(model, "stage_code"):
        q = q.filter(model.stage_code == int(stage_code))
    elif stage_code and model is Archive:
        q = q.filter(Archive.current_stage == int(stage_code))
    if hasattr(model, "submitted_at"):
        if date_from:
            q = q.filter(model.submitted_at >= datetime.combine(values["date_from"], time.min, TZ8))
        if date_to:
            q = q.filter(model.submitted_at < datetime.combine(values["date_to"] + timedelta(days=1), time.min, TZ8))
    return q


def overview(db: Session, actor, **filters) -> dict:
    fkeys = ("batch_id", "college_id", "branch_id", "stage_code", "date_from", "date_to")
    aq = apply_filters(scoped_archives(db.query(Archive), actor, db), Archive, **{k: filters.get(k) for k in fkeys})
    sq = apply_filters(scoped_submissions(db.query(Submission), actor, db), Submission, **{k: filters.get(k) for k in fkeys})
    if filters.get("date_from") or filters.get("date_to"):
        aq = aq.filter(Archive.id.in_(sq.with_entities(Submission.archive_id)))
    archives = aq.count()
    rows = sq.all()
    submissions = len(rows)
    sub_ids = [s.id for s in rows]
    mats = db.query(func.count(Material.id)).filter(Material.submission_id.in_(sub_ids) if sub_ids else Material.id == -1).scalar() or 0
    issues = db.query(Issue).filter(Issue.submission_id.in_(sub_ids) if sub_ids else Issue.id == -1, Issue.is_active.is_(True)).all()
    by_cat = Counter(i.category for i in issues)
    by_sev = Counter(i.severity for i in issues)
    returned = sum(1 for s in rows if s.status == "RETURNED")
    filed = sum(1 for s in rows if s.status == "FILED")
    return_rate = returned / submissions if submissions else 0
    by_stage = []
    from collections import defaultdict
    st = defaultdict(lambda: {"submissions": 0, "filed": 0, "returned": 0})
    for s in rows:
        st[s.stage_code]["submissions"] += 1
        if s.status == "FILED":
            st[s.stage_code]["filed"] += 1
        if s.status == "RETURNED":
            st[s.stage_code]["returned"] += 1
    for code, v in sorted(st.items()):
        by_stage.append({"stage_code": code, **v})
    by_branch = []
    br = defaultdict(lambda: {"submissions": 0, "returned": 0, "issues": 0})
    from models import Org
    names = {o.id: o.name for o in db.query(Org).all()}
    iss_count = Counter(i.submission_id for i in issues)
    for s in rows:
        br[s.branch_id]["submissions"] += 1
        if s.status == "RETURNED":
            br[s.branch_id]["returned"] += 1
        br[s.branch_id]["issues"] += iss_count.get(s.id, 0)
    for bid, v in br.items():
        by_branch.append({
            "branch_id": bid, "branch_name": names.get(bid),
            "submissions": v["submissions"],
            "return_rate": (v["returned"] / v["submissions"]) if v["submissions"] else 0,
            "issues_per_submission": (v["issues"] / v["submissions"]) if v["submissions"] else 0,
        })
    avg_rounds = 0
    if submissions:
        avg_rounds = sum(s.round_no or 1 for s in rows) / submissions
    trend, avg_hours = _review_flow(db, sub_ids)
    return {
        "materials": mats,
        "submissions": submissions,
        "archives": archives,
        "issues_total": len(issues),
        "issues_by_category": dict(by_cat),
        "issues_by_severity": dict(by_sev),
        "return_rate": return_rate,
        "avg_rectification_rounds": avg_rounds,
        "avg_review_hours_by_level": avg_hours,
        "by_stage": by_stage,
        "by_branch": by_branch,
        "trend": trend,
    }


def _review_flow(db: Session, sub_ids: list) -> tuple[list, dict]:
    if not sub_ids:
        return [], {"BRANCH": None, "CROSS": None, "COLLEGE": None, "ORG": None}
    recs = (
        db.query(ReviewRecord)
        .filter(ReviewRecord.submission_id.in_(sub_ids))
        .order_by(ReviewRecord.submission_id, ReviewRecord.created_at, ReviewRecord.id)
        .all()
    )
    days = defaultdict(lambda: {"submitted": 0, "passed": 0, "returned": 0})
    spent = defaultdict(list)
    prev = None
    for r in recs:
        if r.created_at:
            d = days[r.created_at.date().isoformat()]
            if r.action in ("SUBMIT", "RESUBMIT"):
                d["submitted"] += 1
            elif r.action in ("PASS", "FILE"):
                d["passed"] += 1
            elif r.action == "RETURN":
                d["returned"] += 1
        # time at a level = gap since the record that moved the package into it
        if (r.level in ("BRANCH", "CROSS", "COLLEGE", "ORG") and prev is not None
                and prev.submission_id == r.submission_id and prev.created_at and r.created_at):
            spent[r.level].append((r.created_at - prev.created_at).total_seconds() / 3600)
        prev = r
    trend = [{"date": k, **v} for k, v in sorted(days.items())]
    avg = {lv: (round(sum(spent[lv]) / len(spent[lv]), 2) if spent[lv] else None) for lv in ("BRANCH", "CROSS", "COLLEGE", "ORG")}
    return trend, avg


def top_issues(db, actor, limit=10, group_by="rule", **filters) -> list:
    if group_by not in ("rule", "category", "material_type"):
        raise unprocessable("不支持的问题分组方式")
    if not 1 <= int(limit) <= 100:
        raise unprocessable("limit 必须在 1 到 100 之间")
    sq = apply_filters(scoped_submissions(db.query(Submission.id), actor, db), Submission,
                       **{k: filters.get(k) for k in ("batch_id", "college_id", "branch_id", "stage_code", "date_from", "date_to")})
    ids = [x[0] for x in sq.all()]
    q = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.is_active.is_(True))
    items = q.all()
    material_types = _issue_material_types(db, items)
    groups = defaultdict(lambda: {"count": 0, "confirmed": 0, "name": "", "category": ""})
    for i in items:
        if group_by == "category":
            key = i.category
            name = i.category
        elif group_by == "material_type":
            key, name = material_types.get(i.material_id, ("UNASSIGNED", "未关联材料类型"))
        else:
            key = i.rule_code or i.title
            name = i.title
        g = groups[key]
        g["count"] += 1
        g["name"] = name
        g["category"] = i.category
        if i.review_status == "CONFIRMED":
            g["confirmed"] += 1
    total = sum(g["count"] for g in groups.values()) or 1
    out = []
    for k, g in groups.items():
        out.append({"key": k, "name": g["name"], "category": g["category"], "count": g["count"],
                    "ratio": g["count"] / total, "confirmed_count": g["confirmed"]})
    out.sort(key=lambda x: -x["count"])
    return out[: int(limit or 10)]


def _issue_material_types(db, issues) -> dict:
    ids = {i.material_id for i in issues if i.material_id is not None}
    if not ids:
        return {}
    rows = (db.query(Material.id, MaterialType.code, MaterialType.name)
            .outerjoin(MaterialType, Material.type_id == MaterialType.id).filter(Material.id.in_(ids)).all())
    return {mid: (code or "UNCLASSIFIED", name or "未分类材料") for mid, code, name in rows}


def _quality_groups(issues, key_and_name, key_field):
    groups = defaultdict(lambda: {"total": 0, "confirmed": 0, "rejected": 0, "modified": 0, "name": ""})
    for issue in issues:
        key, name = key_and_name(issue)
        group = groups[key]
        group["total"] += 1
        group["name"] = name
        status = issue.review_status.lower()
        if status in ("confirmed", "rejected", "modified"):
            group[status] += 1
    out = []
    for key, group in sorted(groups.items()):
        reviewed = group["confirmed"] + group["rejected"] + group["modified"]
        out.append({key_field: key, **group, "reviewed": reviewed,
                    "precision": group["confirmed"] / reviewed if reviewed else None})
    return out


def ai_quality(db, actor, **filters) -> dict:
    sq = apply_filters(scoped_submissions(db.query(Submission.id), actor, db), Submission,
                       **{k: filters.get(k) for k in FILTER_KEYS})
    ids = [x[0] for x in sq.all()]
    reports = db.query(AiReport).filter(AiReport.submission_id.in_(ids) if ids else AiReport.id == -1, AiReport.status == "DONE").all()
    issues = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.source != "MANUAL").all()
    reviewed = [i for i in issues if i.review_status in ("CONFIRMED", "REJECTED", "MODIFIED")]
    confirmed = [i for i in issues if i.review_status == "CONFIRMED"]
    rejected = [i for i in issues if i.review_status == "REJECTED"]
    modified = [i for i in issues if i.review_status == "MODIFIED"]
    manual = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.source == "MANUAL").count()
    by_rule_out = _quality_groups(issues, lambda i: (i.rule_code or "", i.title), "rule_code")
    material_types = _issue_material_types(db, issues)
    by_material_type = _quality_groups(issues, lambda i: material_types.get(
        i.material_id, ("UNASSIGNED", "未关联材料类型")), "material_type_code")
    # Only filed packages have completed the entire review process. Pending
    # packages cannot yet be called first-pass successes or failures.
    completed = db.query(Submission).filter(Submission.id.in_(ids), Submission.status == "FILED").all()
    returned_ids = {r[0] for r in db.query(ReviewRecord.submission_id).filter(
        ReviewRecord.submission_id.in_(ids), ReviewRecord.action == "RETURN").distinct().all()}
    first_pass = sum(1 for s in completed if (s.round_no or 1) == 1 and s.id not in returned_ids)
    modes = Counter(r.mode for r in reports)
    dur = [r.duration_ms for r in reports if r.duration_ms is not None]
    return {
        "reports": len(reports),
        "materials_checked": sum((r.summary or {}).get("materials_checked") or 0 for r in reports),
        "avg_duration_ms": (sum(dur) / len(dur)) if dur else 0,
        "mode_ratio": dict(modes),
        "ai_issues": len(issues),
        "reviewed": len(reviewed),
        "confirmed": len(confirmed),
        "rejected": len(rejected),
        "modified": len(modified),
        "confirm_rate": (len(confirmed) / len(reviewed)) if reviewed else 0,
        "false_positive_rate": (len(rejected) / len(reviewed)) if reviewed else 0,
        "manual_added": manual,
        "miss_ratio": (manual / (len(issues) + manual)) if (issues or manual) else 0,
        "first_pass_rate": first_pass / len(completed) if completed else None,
        "first_pass_count": first_pass,
        "completed_submissions": len(completed),
        "first_pass_definition": "已备案且未经退回、仅一轮的提交包数 / 已备案提交包数",
        "by_rule": by_rule_out,
        "by_material_type": by_material_type,
        "by_category": dict(Counter(i.category for i in issues)),
    }
