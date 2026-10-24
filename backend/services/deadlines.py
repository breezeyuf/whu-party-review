"""In-app reminders scoped to the current workflow owner, once per deadline."""
from sqlalchemy.dialects.postgresql import insert
from models import Batch, Submission, User, UserRole, CrossReviewPair, Message
from utils import get_setting, now


def scan_deadlines(db, today=None):
    today = today or now().date()
    cfg = get_setting(db, 'notification', {})
    if cfg.get('in_app') is False:
        return 0
    configured = cfg.get('deadline_remind_days', [3, 1])
    days = {max(0, int(d)) for d in (configured if isinstance(configured, list) else [configured])}
    fields = {'DRAFT': 'self_deadline', 'BRANCH_REVIEW': 'branch_deadline',
              'CROSS_REVIEW': 'cross_deadline', 'COLLEGE_REVIEW': 'college_deadline', 'ORG_FILING': 'org_deadline'}
    count = 0
    for sub, batch in db.query(Submission, Batch).join(Batch, Submission.batch_id == Batch.id).filter(Batch.status == 'ACTIVE', Submission.status != 'FILED').all():
        status = sub.return_level if sub.status == 'RETURNED' else sub.status
        # return_level uses review-level names, including BRANCH/CROSS/COLLEGE/ORG.
        status = {'BRANCH':'BRANCH_REVIEW','CROSS':'CROSS_REVIEW','COLLEGE':'COLLEGE_REVIEW','ORG':'ORG_FILING'}.get(status,status)
        field = fields.get(status)
        deadline = getattr(batch, field, None) if field else None
        if deadline is None or (deadline-today).days not in days:
            continue
        if sub.status in ('DRAFT', 'RETURNED'):
            recipients = [sub.archive.student_user_id]
        else:
            role = {'BRANCH_REVIEW':'BRANCH_REVIEWER','CROSS_REVIEW':'CROSS_REVIEWER','COLLEGE_REVIEW':'COLLEGE_REVIEWER','ORG_FILING':'ORG_ADMIN'}[status]
            query = db.query(UserRole.user_id).filter(UserRole.role == role)
            if status == 'BRANCH_REVIEW': query = query.filter(UserRole.org_id == sub.branch_id)
            elif status == 'COLLEGE_REVIEW': query = query.filter(UserRole.org_id == sub.college_id)
            elif status == 'CROSS_REVIEW':
                pair = db.query(CrossReviewPair).filter(CrossReviewPair.batch_id == batch.id, CrossReviewPair.target_branch_id == sub.branch_id).first()
                if not pair: continue
                query = query.filter(UserRole.org_id == pair.reviewer_branch_id)
                if pair.reviewer_user_id: query = query.filter(UserRole.user_id == pair.reviewer_user_id)
            recipients = [r[0] for r in query.all()]
        for uid in set(recipients):
            if not uid or not db.query(User.id).filter(User.id == uid, User.is_active.is_(True)).first(): continue
            key = f'deadline:{sub.id}:{sub.round_no}:{field}:{deadline}:{today}:{uid}'
            result = db.execute(insert(Message).values(user_id=uid, msg_type='DEADLINE',
                title='材料办理截止提醒', content=f'{batch.name}：提交包 #{sub.id} 请于 {deadline.isoformat()} 前完成办理。',
                link_type='submission', link_id=sub.id, dedup_key=key, is_read=False, created_at=now()
            ).on_conflict_do_nothing(index_elements=['dedup_key']).returning(Message.id))
            count += len(result.all())
    return count
