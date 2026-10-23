from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Query, Session

from deps import Actor
from errors import not_found
from models import Archive, CrossReviewPair, Submission
from services.audit import log as audit_log


REVIEWER_ROLES = {"BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"}


def scoped_archives(query: Query, actor: Actor, db: Session) -> Query:
    role, org_id = actor.role, actor.org_id
    if role == "STUDENT":
        return query.filter(Archive.student_user_id == actor.id)
    if role == "BRANCH_REVIEWER":
        return query.filter(Archive.branch_id == org_id)
    if role == "COLLEGE_REVIEWER":
        return query.filter(Archive.college_id == org_id)
    if role in ("ORG_ADMIN", "SYS_ADMIN"):
        return query
    if role == "CROSS_REVIEWER":
        assigned = db.query(CrossReviewPair.id).filter(
            CrossReviewPair.reviewer_branch_id == org_id,
            CrossReviewPair.target_branch_id == Archive.branch_id,
            CrossReviewPair.batch_id == Archive.batch_id,
            (CrossReviewPair.reviewer_user_id.is_(None)) | (CrossReviewPair.reviewer_user_id == actor.id),
        ).exists()
        return query.filter(assigned, Archive.branch_id != org_id)
    return query.filter(Archive.id == -1)


def scoped_submissions(query: Query, actor: Actor, db: Session) -> Query:
    role, org_id = actor.role, actor.org_id
    if role == "STUDENT":
        return query.join(Archive, Archive.id == Submission.archive_id).filter(Archive.student_user_id == actor.id)
    if role == "BRANCH_REVIEWER":
        return query.filter(Submission.branch_id == org_id)
    if role == "COLLEGE_REVIEWER":
        return query.filter(Submission.college_id == org_id)
    if role in ("ORG_ADMIN", "SYS_ADMIN"):
        return query
    if role == "CROSS_REVIEWER":
        assigned = db.query(CrossReviewPair.id).filter(
            CrossReviewPair.reviewer_branch_id == org_id,
            CrossReviewPair.target_branch_id == Submission.branch_id,
            CrossReviewPair.batch_id == Submission.batch_id,
            (CrossReviewPair.reviewer_user_id.is_(None)) | (CrossReviewPair.reviewer_user_id == actor.id),
        ).exists()
        return query.filter(assigned, Submission.branch_id != org_id)
    return query.filter(Submission.id == -1)


def scoped_jobs(db: Session, actor: Actor):
    """任务列表/详情的数据范围（原 routers/jobs.py::_scoped_jobs，逻辑不变）。

    ZIP 确认入库也用它取任务，保证“看不到的任务”一律 404，不泄露他人任务。
    """
    from sqlalchemy import and_, or_

    from models import Job, Material, MaterialVersion

    query = db.query(Job)
    if actor.role in ("SYS_ADMIN", "ORG_ADMIN"):
        return query
    if actor.role == "STUDENT":
        return query.filter(Job.created_by == actor.id)
    submissions = scoped_submissions(db.query(Submission.id), actor, db)
    versions = db.query(MaterialVersion.id).join(Material).filter(Material.submission_id.in_(submissions))
    return query.filter(or_(
        Job.created_by == actor.id,
        and_(Job.target_type == "submission", Job.target_id.in_(submissions)),
        and_(Job.target_type == "material_version", Job.target_id.in_(versions)),
    ))


def ensure_archive_access(db: Session, actor: Actor, archive_id: int, request=None) -> Archive:
    q = scoped_archives(db.query(Archive), actor, db).filter(Archive.id == archive_id)
    row = q.first()
    if not row:
        if request:
            audit_log(db, actor, "ACCESS_DENIED", "archive", str(archive_id), {"reason": "scope"}, request)
        raise not_found()
    return row


def ensure_submission_access(db: Session, actor: Actor, submission_id: int, request=None) -> Submission:
    q = scoped_submissions(db.query(Submission), actor, db).filter(Submission.id == submission_id)
    row = q.first()
    if not row:
        if request:
            audit_log(db, actor, "ACCESS_DENIED", "submission", str(submission_id), {"reason": "scope"}, request)
        raise not_found()
    return row


def can_review(submission: Submission, actor: Actor, db: Session) -> bool:
    status = submission.status
    role, org_id = actor.role, actor.org_id
    if status == "BRANCH_REVIEW" and role == "BRANCH_REVIEWER" and submission.branch_id == org_id:
        return True
    if status == "COLLEGE_REVIEW" and role == "COLLEGE_REVIEWER" and submission.college_id == org_id:
        return True
    if status == "ORG_FILING" and role == "ORG_ADMIN":
        return True
    if status == "CROSS_REVIEW" and role == "CROSS_REVIEWER":
        pair = (
            db.query(CrossReviewPair)
            .filter(
                CrossReviewPair.batch_id == submission.batch_id,
                CrossReviewPair.target_branch_id == submission.branch_id,
                CrossReviewPair.reviewer_branch_id == org_id,
                (CrossReviewPair.reviewer_user_id.is_(None)) | (CrossReviewPair.reviewer_user_id == actor.id),
            )
            .first()
        )
        if not pair:
            return False
        if pair.reviewer_user_id and pair.reviewer_user_id != actor.id:
            return False
        return submission.branch_id != org_id
    return False


def current_level(submission: Submission) -> Optional[str]:
    from utils import LEVEL_BY_STATUS

    if submission.status == "RETURNED":
        return submission.return_level
    return LEVEL_BY_STATUS.get(submission.status)


def org_scope_ids(db: Session, actor: Actor) -> Optional[list[int]]:
    if actor.role in ("ORG_ADMIN", "SYS_ADMIN"):
        return None
    if actor.role == "COLLEGE_REVIEWER":
        from models import Org

        ids = [actor.org_id]
        children = db.query(Org.id).filter(Org.parent_id == actor.org_id).all()
        ids.extend(r[0] for r in children)
        return ids
    return [actor.org_id]
