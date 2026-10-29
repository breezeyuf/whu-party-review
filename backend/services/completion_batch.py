"""Shared completion notices for synchronous requests and authorized queued jobs."""
from datetime import date

from deps import Actor
from errors import forbidden, unprocessable
from models import Material, User, UserRole
from services.scope import ensure_submission_access
from services.notices import create_completion_notice
from services.timeline import node_map_for_archive

ROLES = ('BRANCH_REVIEWER', 'COLLEGE_REVIEWER', 'ORG_ADMIN')


def validate_batch(body):
    ids = body.get('submission_ids')
    if not isinstance(ids, list) or not ids or len(ids) > 500 or any(type(i) is not int or i < 1 for i in ids):
        raise unprocessable('请选择 1–500 个有效提交包')
    if type(body.get('send', True)) is not bool or type(body.get('background', False)) is not bool:
        raise unprocessable('发送和后台处理选项须为布尔值')
    if body.get('note') is not None and not isinstance(body['note'], str):
        raise unprocessable('备注须为文字')
    if body.get('deadline') is not None:
        try:
            if date.fromisoformat(body['deadline']).isoformat() != body['deadline']:
                raise ValueError()
        except (ValueError, TypeError):
            raise unprocessable('截止日期须为有效的 YYYY-MM-DD')
    return list(dict.fromkeys(ids))


def generate_batch(db, actor, body):
    if actor.role not in ROLES:
        raise forbidden()
    ids = validate_batch(body)
    # Validate the whole scope before creating any notices.
    submissions = [ensure_submission_access(db, actor, sid) for sid in ids]
    created, skipped = [], []
    from ai.checks.completeness import run_completeness
    from ai.checks.timeline import nodes_from_map
    for sub in submissions:
        mats = db.query(Material).filter(Material.submission_id == sub.id, Material.status == 'ACTIVE').all()
        nodes = nodes_from_map(node_map_for_archive(db, sub.archive_id))
        comp, _, _ = run_completeness(db, sub, mats, nodes)
        notice = create_completion_notice(db, sub, actor, comp, body.get('deadline'), body.get('send', True), body.get('note'))
        if notice:
            created.append({'notice_id': notice.id, 'submission_id': sub.id, 'student_name': sub.archive.real_name, 'missing_total': comp.get('missing_total')})
        else:
            skipped.append({'submission_id': sub.id, 'reason': '材料已齐全'})
    return {'created': created, 'skipped': skipped}


def run_notice_batch(db, job):
    params = job.params or {}
    user = db.query(User).filter(User.id == job.created_by, User.is_active.is_(True)).first()
    grant = db.query(UserRole).filter(UserRole.user_id == job.created_by,
        UserRole.role == params.get('actor_role'), UserRole.org_id == params.get('actor_org_id')).first()
    if not user or not grant or grant.role not in ROLES:
        raise forbidden('发起人的通知权限已失效')
    actor = Actor(user, grant.role, grant.org_id, [grant], '', 'NOTICE_BATCH')
    # Exceptions must not leave partially generated notices when worker records failure.
    with db.begin_nested():
        result = generate_batch(db, actor, params)
        job.total = len(validate_batch(params))
        job.done_count = job.total
        job.failed_count = 0
        job.result = result
        job.stage_text = '补全提示处理完成'
        db.flush()
    return result
