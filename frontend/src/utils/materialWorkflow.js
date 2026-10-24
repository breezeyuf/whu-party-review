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

// stageCode 为确认区选择的导入阶段：选了才作为请求级 stage_code 提交，未选时由后端
// 依次取上传时选择的阶段、档案当前阶段
export function batchAssignmentBody(items, drafts = {}, stageCode) {
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
  const body = { assignments, skip_item_ids }
  const stage = positiveInteger(stageCode)
  if (stage) body.stage_code = stage
  return body
}

// 接口已回写 job.result，此处用于即时更新：以接口返回的条目为准（已导入的条目不会被改成跳过），
// 接口未返回的跳过项按已跳过显示
export function mergeBatchItems(items, result, skippedIds = []) {
  const changed = new Map((result?.items || []).map((item) => [String(item.item_id), item.status === "IMPORTED" ? { ...item, error: null } : item]))
  const skipped = new Set(skippedIds.map(String))
  return items.map((item) => changed.get(String(item.item_id))
    || (skipped.has(String(item.item_id)) ? { ...item, status: "SKIPPED", error: null } : item))
}
