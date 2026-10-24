export const isAiPending = (submission) => ["QUEUED", "RUNNING"].includes(submission?.ai_status)

export function studentMaterials(groups = []) {
  const materials = groups.flatMap((group) => [
    ...(group.checklist || []).flatMap((item) => item.materials || []),
    ...(group.unclassified || []), ...(group.extra || []),
  ])
  return [...new Map(materials.map((material) => [material.id, material])).values()]
}

export const pendingParseCount = (groups) => studentMaterials(groups).filter((material) => ["PENDING", "QUEUED", "RUNNING"].includes(material.current_version?.parse_status)).length

// Match submit_package: a returned package gates on every confirmed issue;
// an initial draft gates on non-rejected blocking issues.
export function pendingStudentReplies(submission, issues = []) {
  return issues.filter((issue) => issue.is_active !== false && !issue.response_type && (
    submission?.status === "RETURNED"
      ? ["CONFIRMED", "MODIFIED"].includes(issue.review_status)
      : issue.severity === "BLOCK" && issue.review_status !== "REJECTED"
  ))
}

export function studentSubmitReason(submission, issues, { ready = true, taskPending = false } = {}) {
  if (!submission?.can?.submit) return "当前状态或角色不可提交。"
  if (!ready) return "正在读取问题与提交状态，请稍候。"
  if (taskPending || isAiPending(submission)) return "检查任务正在进行，请等待完成。"
  if (submission.status === "DRAFT" && (!submission.latest_report || (submission.latest_report.status && submission.latest_report.status !== "DONE") || submission.latest_report.is_stale || submission.ai_status === "FAILED")) {
    return "请先完成有效的 AI 自查；材料或时间节点变更后需重新自查。"
  }
  const count = pendingStudentReplies(submission, issues).length
  if (count) return `还有 ${count} 条${submission.status === "RETURNED" ? "已确认问题" : "阻断问题"}未回复，请逐条整改或填写情况说明。`
  return ""
}

export function issueMaterialId(issue) {
  return issue?.material_id || issue?.location?.material_id || null
}

export const refreshStudentRequests = (...requests) => Promise.allSettled(requests.map((request) => request.reload()))
