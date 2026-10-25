"""Server-side batch comparison; other students' text never enters issue output."""
from sqlalchemy.orm import aliased
from models import Archive, Material, MaterialVersion, ParseResult, Submission
from ai.evidence import effective_text


def batch_candidates(db, submission, material):
    if not submission.batch_id or not material.type_id:
        return
    other = aliased(Archive)
    query = (db.query(Material.id, MaterialVersion.id, ParseResult)
             .join(Submission, Submission.id == Material.submission_id)
             .join(other, other.id == Material.archive_id)
             .join(MaterialVersion, MaterialVersion.id == Material.current_version_id)
             .join(ParseResult, ParseResult.version_id == MaterialVersion.id)
             .filter(Submission.batch_id == submission.batch_id, Submission.stage_code == submission.stage_code,
                     Material.status == 'ACTIVE', Material.type_id == material.type_id,
                     MaterialVersion.parse_status == 'DONE', Material.archive_id != submission.archive_id,
                     other.student_user_id != submission.archive.student_user_id)
             .order_by(Material.id))
    for mid, vid, parsed in query.yield_per(100):
        yield mid, vid, effective_text(parsed)


def compare_batch(db, submission, material, text, threshold):
    from ai.checks.content import _ngrams, _jaccard
    own = _ngrams(text)
    if not own or not submission.batch_id:
        return None
    best, total = 0.0, 0
    for _, _, candidate in batch_candidates(db, submission, material):
        if not candidate.strip():
            continue
        total += 1
        best = max(best, _jaccard(own, _ngrams(candidate)))
    return {'score': best, 'count': total} if total else None
