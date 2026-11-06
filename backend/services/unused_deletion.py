"""Delete mistaken, unused records without purging business or audit history."""
from sqlalchemy import delete, select, or_, and_
from sqlalchemy.exc import IntegrityError

from database import Base
from errors import conflict, forbidden, not_found
from models import Archive, ArchiveTimeNode, AuditLog, Job, Submission, User, UserRole
from services.audit import log
from services.scope import ensure_archive_access
from services.users import can_manage_account


def _referenced(db, parent, ids, *, skip=()):
    # SET NULL is also a business reference: do not silently erase authorship.
    for table in Base.metadata.tables.values():
        if table.name in skip:
            continue
        for fk in table.foreign_keys:
            if fk.column.table.name == parent and db.execute(
                select(fk.parent).where(fk.parent.in_(ids)).limit(1)
            ).first():
                return True
    return False


def delete_unused_user(db, actor, uid):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    user = db.query(User).filter(User.id == uid).with_for_update().first()
    if not user:
        raise not_found("用户不存在或已删除")
    if not can_manage_account(db, actor, user):
        raise forbidden("无权删除此账号")
    if actor.id == uid:
        raise conflict("不能删除当前登录账号")
    if user.is_active and any(g.role == "SYS_ADMIN" for g in user.roles):
        other_admin = db.query(User.id).join(UserRole).filter(
            UserRole.role == "SYS_ADMIN", User.is_active.is_(True), User.id != uid,
        ).first()
        if not other_admin:
            raise conflict("不能删除最后一个启用的系统管理员")
    if db.query(Archive.id).filter(Archive.student_user_id == uid).first():
        raise conflict("该账号已关联发展档案，请先在发展档案中删除空档案；已有办理记录请停用账号")
    if (user.last_login_at or db.query(AuditLog.id).filter(AuditLog.user_id == uid).first()
            or _referenced(db, "users", [uid], skip=("user_roles",))):
        raise conflict("该账号已有使用、分配或业务记录，不能删除；可在编辑中停用账号")
    try:
        with db.begin_nested():
            db.execute(delete(User).where(User.id == uid), execution_options={"synchronize_session": False})
            log(db, actor, "USER_DELETE", "user", uid, {"username": user.username})
    except IntegrityError:
        raise conflict("账号已被关联，请刷新后检查档案或停用账号")


def delete_empty_archive(db, actor, aid, request=None):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    ensure_archive_access(db, actor, aid, request)
    archive = db.query(Archive).filter(Archive.id == aid).with_for_update().first()
    if not archive:
        raise not_found("档案不存在或已删除")
    subs = db.query(Submission).filter(Submission.archive_id == aid).order_by(Submission.id).with_for_update().all()
    ids = [s.id for s in subs]
    message = "档案已有材料、日期或办理记录，不能删除；仅支持删除尚未办理的空档案"
    if archive.status != "ACTIVE" or any(
        s.status != "DRAFT" or s.round_no != 1 or s.ai_status != "NONE"
        or s.latest_report_id or s.ai_job_id or s.submitted_at or s.filed_at or s.level_entered_at
        for s in subs
    ):
        raise conflict(message)
    if (_referenced(db, "archives", [aid], skip=("submissions", "archive_time_nodes"))
            or (ids and _referenced(db, "submissions", ids))
            or db.query(Job.id).filter(or_(
                and_(Job.target_type == "archive", Job.target_id == aid),
                and_(Job.target_type == "submission", Job.target_id.in_(ids)),
                *(Job.params.contains({"submission_ids": [sid]}) for sid in ids),
            )).first()):
        raise conflict(message)
    nodes = db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == aid).all()
    fields = ("value_date", "value_end_date", "hours", "seq_count", "source_count",
              "source_extraction_id", "has_conflict", "corrected_date", "corrected_end_date",
              "corrected_hours", "correction_reason", "corrected_by", "corrected_at", "locked", "locked_stage")
    if any(any(getattr(n, k) is not None and getattr(n, k) != 0 and getattr(n, k) != "" for k in fields) for n in nodes):
        raise conflict(message)
    try:
        with db.begin_nested():
            db.execute(delete(Archive).where(Archive.id == aid), execution_options={"synchronize_session": False})
            log(db, actor, "ARCHIVE_DELETE", "archive", aid,
                {"student_no": archive.student_no, "student_account_retained": True})
    except IntegrityError:
        raise conflict("档案已产生关联记录，请刷新后检查，不能删除办理历史")
