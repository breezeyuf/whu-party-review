"""Server-side batch comparison; other students' text never enters issue output."""
from hashlib import sha256

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
    candidates = []
    for _, _, candidate in batch_candidates(db, submission, material):
        if not candidate.strip():
            continue
        total += 1
        score = _jaccard(own, _ngrams(candidate))
        best = max(best, score)
        # Keep the exact comparison scores and text fingerprints in the report,
        # without disclosing another student's text, name, or material ID.
        candidates.append({'text_sha256': sha256(candidate.encode('utf-8')).hexdigest(), 'score': score})
    if not total:
        return None
    return {
        'score': best,
        'count': total,
        'comparison': {
            'algorithm': 'char_3gram_jaccard',
            'own_text_sha256': sha256(text.encode('utf-8')).hexdigest(),
            'candidates': sorted(candidates, key=lambda item: (item['text_sha256'], item['score'])),
        },
    }
