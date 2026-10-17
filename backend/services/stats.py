from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import AiReport, Archive, Issue, Material, ReviewRecord, Submission
from services.scope import scoped_archives, scoped_submissions
from utils import as_date


def apply_filters(q, model, batch_id=None, college_id=None, branch_id=None, stage_code=None, date_from=None, date_to=None):
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
            d1 = as_date(date_from)
            if d1:
                q = q.filter(model.submitted_at >= d1)
        if date_to:
            d2 = as_date(date_to)
            if d2:
                q = q.filter(model.submitted_at < d2 + timedelta(days=1))
    return q


def overview(db: Session, actor, **filters) -> dict:
    fkeys = ("batch_id", "college_id", "branch_id", "stage_code", "date_from", "date_to")
    aq = apply_filters(scoped_archives(db.query(Archive), actor, db), Archive, **{k: filters.get(k) for k in fkeys})
    sq = apply_filters(scoped_submissions(db.query(Submission), actor, db), Submission, **{k: filters.get(k) for k in fkeys})
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
    sq = apply_filters(scoped_submissions(db.query(Submission.id), actor, db), Submission,
                       **{k: filters.get(k) for k in ("batch_id", "college_id", "branch_id", "stage_code", "date_from", "date_to")})
    ids = [x[0] for x in sq.all()]
    q = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.is_active.is_(True))
    items = q.all()
    groups = defaultdict(lambda: {"count": 0, "confirmed": 0, "name": "", "category": ""})
    for i in items:
        if group_by == "category":
            key = i.category
            name = i.category
        elif group_by == "material_type":
            key = str(i.material_id)
            name = str(i.material_id)
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


def ai_quality(db, actor, **filters) -> dict:
    sq = apply_filters(scoped_submissions(db.query(Submission.id), actor, db), Submission,
                       **{k: filters.get(k) for k in ("batch_id", "college_id", "branch_id", "stage_code")})
    ids = [x[0] for x in sq.all()]
    reports = db.query(AiReport).filter(AiReport.submission_id.in_(ids) if ids else AiReport.id == -1, AiReport.status == "DONE").all()
    issues = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.source != "MANUAL").all()
    reviewed = [i for i in issues if i.review_status != "PENDING"]
    confirmed = [i for i in issues if i.review_status == "CONFIRMED"]
    rejected = [i for i in issues if i.review_status == "REJECTED"]
    modified = [i for i in issues if i.review_status == "MODIFIED"]
    manual = db.query(Issue).filter(Issue.submission_id.in_(ids) if ids else Issue.id == -1, Issue.source == "MANUAL").count()
    by_rule = defaultdict(lambda: {"total": 0, "confirmed": 0, "rejected": 0, "modified": 0, "name": ""})
    for i in issues:
        g = by_rule[i.rule_code or ""]
        g["total"] += 1
        g["name"] = i.title
        if i.review_status == "CONFIRMED":
            g["confirmed"] += 1
        if i.review_status == "REJECTED":
            g["rejected"] += 1
        if i.review_status == "MODIFIED":
            g["modified"] += 1
    by_rule_out = []
    for code, g in by_rule.items():
        prec = g["confirmed"] / g["total"] if g["total"] else 0
        by_rule_out.append({"rule_code": code, "name": g["name"], **g, "precision": prec})
    modes = Counter(r.mode for r in reports)
    dur = [r.duration_ms for r in reports if r.duration_ms]
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
        "first_pass_rate": 0,
        "by_rule": by_rule_out,
        "by_material_type": [],
        "by_category": dict(Counter(i.category for i in issues)),
    }
