export const JOB_TERMINAL = new Set(["SUCCEEDED", "FAILED", "PARTIAL", "CANCELLED"])
export const PARSE_PENDING = new Set(["PENDING", "QUEUED", "RUNNING"])

export function positiveInteger(value) {
  const number = Number(value)
  return Number.isSafeInteger(number) && number > 0 ? number : null
}

export function validBbox(value) {
  if (!Array.isArray(value) || value.length !== 4) return null
  const box = value.map(Number)
  return box.every(Number.isFinite) && box[2] > box[0] && box[3] > box[1] ? box : null
}

// Issues store their version on the issue itself; timeline sources use version_no.
export function materialFocus({ issue, searchParams, versions = [], currentVersion }) {
  const location = issue?.location || {}
  const versionNo = positiveInteger(searchParams?.get("version_no"))
  const versionId = positiveInteger(issue?.material_version_id || location.version_id)
    || positiveInteger(searchParams?.get("version_id"))
    || versions.find((version) => Number(version.version_no) === versionNo)?.id
    || currentVersion?.id
  let queryBox
  try { queryBox = JSON.parse(searchParams?.get("bbox") || "null") } catch { queryBox = null }
  return {
    versionId,
    page: positiveInteger(location.page_no || location.page) || positiveInteger(searchParams?.get("page")) || 1,
    bbox: validBbox(location.bbox) || validBbox(queryBox),
  }
}

export function batchDraft(item, draft = {}) {
  return {
    archive_id: draft.archive_id ?? item.matched_archive?.id ?? "",
    material_type_id: draft.material_type_id ?? "",
    skip: !!draft.skip,
  }
}

export function batchAssignmentBody(items, drafts = {}) {
  const assignments = []
  const skip_item_ids = []
  for (const item of items) {
    if (["IMPORTED", "SKIPPED"].includes(item.status)) continue
    const draft = batchDraft(item, drafts[item.item_id])
    if (draft.skip) { skip_item_ids.push(item.item_id); continue }
    const archiveId = positiveInteger(draft.archive_id)
    if (!archiveId) continue
    const assignment = { item_id: item.item_id, archive_id: archiveId }
    const typeId = positiveInteger(draft.material_type_id)
    if (typeId) assignment.material_type_id = typeId
    assignments.push(assignment)
  }
  return { assignments, skip_item_ids }
}

// The assignment endpoint returns changed rows, but does not update job.result.
export function mergeBatchItems(items, result, skippedIds = []) {
  const changed = new Map((result?.items || []).map((item) => [String(item.item_id), item.status === "IMPORTED" ? { ...item, error: null } : item]))
  const skipped = new Set(skippedIds.map(String))
  return items.map((item) => skipped.has(String(item.item_id))
    ? { ...item, status: "SKIPPED", error: null }
    : changed.get(String(item.item_id)) || item)
}
