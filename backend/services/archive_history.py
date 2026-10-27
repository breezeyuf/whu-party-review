"""Development history assembled from persisted events, including old records."""
from models import (AiReport, AuditLog, Issue, Material, MaterialVersion, Notice,
                    ReviewRecord, Submission, TimeNodeDef, User)
from services.scope import scoped_submissions


def archive_history(db, archive, actor, stage_code=None):
    items = []
    submissions = scoped_submissions(db.query(Submission), actor, db).filter(Submission.archive_id == archive.id)
    if stage_code is not None:
        submissions = submissions.filter(Submission.stage_code == stage_code)
    stages = {s.id: s.stage_code for s in submissions.all()}
    users = {}

    def name(uid, fallback=None):
        if uid and uid not in users:
            user = db.get(User, uid)
            users[uid] = user.real_name if user else None
        return users.get(uid) or fallback

    def append(time, kind, stage, title, detail, actor_name, link_type, link_id, **extra):
        if stage_code is not None and stage != stage_code:
            return
        items.append({"time": time.isoformat() if time else None, "kind": kind,
                      "stage_code": stage, "title": title, "detail": detail,
                      "actor_name": actor_name, "link_type": link_type, "link_id": link_id, **extra})

    materials = {m.id: m for m in db.query(Material).filter(Material.submission_id.in_(stages)).all()}
    for version in db.query(MaterialVersion).filter(MaterialVersion.material_id.in_(materials)).order_by(MaterialVersion.id).all():
        material = materials[version.material_id]
        append(version.uploaded_at, "UPLOAD", material.stage_code,
               f"上传 {material.title}（第 {version.version_no} 版）", version.change_note,
               name(version.uploaded_by), "material", material.id, version_id=version.id)

    for report in db.query(AiReport).filter(AiReport.submission_id.in_(stages)).order_by(AiReport.id).all():
        status = {"DONE": "已完成", "FAILED": "失败", "RUNNING": "进行中"}.get(report.status, report.status)
        # Do not expose unreviewed findings or raw provider errors through history.
        append(report.finished_at or report.started_at, "AI_REPORT", stages[report.submission_id],
               f"AI 检查报告 #{report.report_no} · {status}", None, name(report.triggered_by, "系统"),
               "submission", report.submission_id, report_id=report.id, report_no=report.report_no)

    filed = set()
    for record in db.query(ReviewRecord).filter(ReviewRecord.submission_id.in_(stages)).order_by(ReviewRecord.id).all():
        is_filed = record.action == "FILE" or record.to_status == "FILED"
        if is_filed:
            filed.add(record.submission_id)
        append(record.created_at, "FILED" if is_filed else "REVIEW", stages[record.submission_id],
               record.action, record.comment, record.reviewer_name, "submission", record.submission_id,
               action=record.action, level=record.level, round_no=record.round_no)
    # Imported/demo archives can be filed without a review record.
    for sub in db.query(Submission).filter(Submission.id.in_(stages), Submission.filed_at.is_not(None)).all():
        if sub.id not in filed:
            append(sub.filed_at, "FILED", sub.stage_code, "FILE", None,
                   name(sub.filed_by), "submission", sub.id, action="FILE")

    notices = db.query(Notice).filter(Notice.submission_id.in_(stages))
    if actor.role == "STUDENT":
        notices = notices.filter(Notice.status == "SENT", Notice.student_user_id == actor.id)
    for notice in notices.order_by(Notice.id).all():
        append(notice.sent_at or notice.created_at, "NOTICE", stages[notice.submission_id], notice.title,
               "通知草稿" if notice.status == "DRAFT" else None,
               name(notice.created_by), "notice", notice.id)

    issues = {str(i.id): i for i in db.query(Issue).filter(Issue.submission_id.in_(stages)).all()}
    logged_responses = {}
    response_logs = db.query(AuditLog).filter(AuditLog.action == "ISSUE_RESPONSE", AuditLog.object_type == "issue",
                                             AuditLog.object_id.in_(issues)).order_by(AuditLog.id).all()
    for event in response_logs:
        issue = issues[event.object_id]
        detail = event.detail or {}
        logged_responses[event.object_id] = event.created_at
        append(event.created_at, "ISSUE_RESPONSE", stages[issue.submission_id],
               "提交整改回复", detail.get("response_text"), name(event.user_id, event.username),
               "submission", issue.submission_id, issue_id=issue.id)
    for iid, issue in issues.items():
        # Older installations store only the last reply on the issue. Preserve it
        # when no audit event represents it; do not duplicate new logged replies.
        logged_at = logged_responses.get(iid)
        if issue.responded_at and (not logged_at or issue.responded_at > logged_at):
            append(issue.responded_at, "ISSUE_RESPONSE", stages[issue.submission_id],
                   "提交整改回复", issue.response_text, name(archive.student_user_id),
                   "submission", issue.submission_id, issue_id=issue.id)

    definitions = {d.code: d for d in db.query(TimeNodeDef).all()}
    for event in db.query(AuditLog).filter(AuditLog.action == "NODE_CORRECTION", AuditLog.object_type == "archive",
                                          AuditLog.object_id == str(archive.id)).order_by(AuditLog.id).all():
        detail = event.detail or {}
        node = detail.get("node")
        definition = definitions.get(node)
        stage = detail.get("stage_code", definition.stage_code if definition else None)
        node_name = detail.get("node_name") or (definition.name if definition else node or "时间节点")
        append(event.created_at, "NODE_CORRECTION", stage,
               f"{'撤销校正' if detail.get('clear') else '校正'} {node_name}", detail.get("reason"),
               name(event.user_id, event.username), "archive", archive.id)
    # Editing a date extracted from a material is also a node correction.
    for event in db.query(AuditLog).filter(AuditLog.action == "PARSE_CORRECT", AuditLog.object_type == "material",
                                          AuditLog.object_id.in_([str(mid) for mid in materials])).order_by(AuditLog.id).all():
        detail = event.detail or {}
        if not detail.get("extractions"):
            continue
        material = materials[int(event.object_id)]
        append(event.created_at, "NODE_CORRECTION", material.stage_code,
               f"校正 {material.title} 的时间节点", detail.get("reason"), name(event.user_id, event.username),
               "material", material.id, version_id=detail.get("version_id"))

    items.sort(key=lambda item: item["time"] or "", reverse=True)
    return items
