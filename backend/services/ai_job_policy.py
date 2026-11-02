"""Shared, live authorization for AI enqueue, retries and worker execution."""
from deps import Actor
from errors import AppError
from models import Job, Org, Submission, User, UserRole
from services.scope import scoped_submissions
from services.workflow import can_actions


class AiJobRejected(AppError):
    def __init__(self, message, status=403):
        super().__init__(status, status * 100, message)


def actor_params(actor):
    return {"actor_role": actor.role, "actor_org_id": actor.org_id}


def lock_submission(db, sid):
    sub = db.query(Submission).filter(Submission.id == sid).with_for_update().populate_existing().first()
    if not sub:
        raise AiJobRejected("提交包已不存在，不能重新检查")
    return sub


def require_actor(db, sub, actor):
    # The submission lock serializes this decision with normal review/file operations.
    user = db.query(User).filter(User.id == actor.id).populate_existing().first()
    grant = db.query(UserRole).join(Org, Org.id == UserRole.org_id).filter(
        UserRole.user_id == actor.id, UserRole.role == actor.role,
        UserRole.org_id == actor.org_id, Org.is_active.is_(True)).first()
    visible = scoped_submissions(db.query(Submission), actor, db).filter(Submission.id == sub.id).first()
    if (not user or not user.is_active or not grant or not visible
            or not can_actions(db, sub, actor)["ai_check"]):
        raise AiJobRejected("当前权限或审核状态不允许重新检查，请刷新办理页面")


def job_actor(db, job, sub):
    user = db.query(User).filter(User.id == job.created_by).populate_existing().first()
    if not user or not user.is_active:
        raise AiJobRejected("原任务发起人已不存在或已停用")
    params = job.params or {}
    grants = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    if params.get("actor_role"):
        grants = [g for g in grants if g.role == params["actor_role"] and g.org_id == params.get("actor_org_id")]
    elif params.get("trigger_type") == "SELF_CHECK":
        grants = [g for g in grants if g.role == "STUDENT"]
    else:
        grants = [g for g in grants if g.role in ("BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN")]
    candidates = []
    for grant in grants:
        actor = Actor(user, grant.role, grant.org_id, grants, "", "worker")
        try:
            require_actor(db, sub, actor)
            candidates.append(actor)
        except AiJobRejected:
            pass
    # Old jobs have no explicit identity. Never silently choose another identity.
    if len(candidates) != 1:
        raise AiJobRejected("原任务身份已失效或不明确，请从当前办理页面重新发起检查")
    return candidates[0]


def require_no_other_job(db, sub, job=None):
    excluded = [x for x in (getattr(job, "id", None), getattr(job, "parent_id", None)) if x]
    active = db.query(Job).filter(Job.status.in_(("QUEUED", "RUNNING")), ~Job.id.in_(excluded))
    if (active.filter(Job.job_type == "AI_CHECK", Job.target_type == "submission", Job.target_id == sub.id).first()
            or active.filter(Job.job_type == "BATCH_AI_CHECK", Job.params["submission_ids"].contains([sub.id])).first()):
        raise AiJobRejected("该提交包已有排队或运行中的检查任务，请等待完成", 409)


def validate_ai_job(db, job, retry_actor=None):
    sid = (job.params or {}).get("submission_id") or job.target_id
    sub = lock_submission(db, sid)
    job_actor(db, job, sub)
    if retry_actor:
        require_actor(db, sub, retry_actor)
    require_no_other_job(db, sub, job)
    return sub
