export const sameId = (a, b) => a != null && b != null && String(a) === String(b)

// The current submissions endpoint accepts these filters but does not apply
// has_block=false or due_within_days. Filter the complete result, then paginate.
export async function loadReviewTasks(fetchPage, query) {
  const noBlocks = query.has_block === "false" || query.has_block === false
  const hasDue = query.due_within_days != null && query.due_within_days !== ""
  if (hasDue && !/^\d+$/.test(String(query.due_within_days))) throw new Error("截止天数须为 0 或正整数")
  if (!noBlocks && !hasDue) return fetchPage(query)
  const params = { ...query, page: 1, page_size: 200 }
  delete params.due_within_days
  if (noBlocks) delete params.has_block
  const first = await fetchPage(params)
  const all = [...(first.items || [])]
  const size = first.page_size || 200
  for (let page = 2; all.length < first.total; page += 1) {
    const next = await fetchPage({ ...params, page, page_size: size })
    if (!next.items?.length) throw new Error("待办数据未完整加载，请重试")
    all.push(...next.items)
  }
  const items = all.filter((row) => (!noBlocks || !(row.issue_counts?.BLOCK > 0))
    && (!hasDue || (row.days_left != null && row.days_left <= Number(query.due_within_days))))
  const pageSize = Math.min(200, Math.max(1, Number(query.page_size) || 20))
  const page = Math.min(Math.max(1, Number(query.page) || 1), Math.max(1, Math.ceil(items.length / pageSize)))
  return { ...first, items: items.slice((page - 1) * pageSize, page * pageSize), total: items.length, page, page_size: pageSize }
}

export async function loadAllReviewIssues(fetchPage) {
  const first = await fetchPage({ active: true, page: 1, page_size: 200 })
  const items = [...(first.items || [])]
  // Current API returns all issues; also handle paginated deployments safely.
  for (let page = 2; first.total != null && items.length < first.total; page += 1) {
    const next = await fetchPage({ active: true, page, page_size: first.page_size || 200 })
    if (!next.items?.length) throw new Error("问题清单未完整加载，请重试")
    items.push(...next.items)
  }
  return { ...first, items }
}

export function reportBlockReason(submission) {
  const report = submission?.latest_report
  if (["QUEUED", "RUNNING"].includes(submission?.ai_status)) return "AI 检查正在排队或运行，请等待完成。"
  if (submission?.ai_status === "FAILED") return "AI 检查失败，请查看任务错误并重试。"
  if (!report) return "还没有 AI 报告，请先发起 AI 审核。"
  if (report.is_stale || (report.status && report.status !== "DONE")) return "报告已过期或未完成，请重新运行 AI 审核。"
  return ""
}

export function passBlockReason(submission, issues, issuesReady = true) {
  const reportReason = reportBlockReason(submission)
  if (reportReason) return reportReason
  if (!issuesReady) return "问题清单尚未完整加载，暂不能通过或备案。"
  if (issues.some((i) => i.is_active !== false && i.severity === "BLOCK" && i.review_status === "PENDING")) return "仍有待人工处理的阻断问题，请先确认、修改或驳回。"
  const report = submission.latest_report
  if (report.handover_status === "REQUIRED") return "报告需要人工接管，请先提交人工结论。"
  if (report.handover_status !== "NOT_REQUIRED" && !(report.handover_status === "DONE" && report.effective_recommendation)) return "人工审核结论未完成，请刷新后重试。"
  return ""
}

export function issueLocation(issue, material) {
  const loc = issue?.location || {}
  return {
    materialId: issue?.material_id || loc.material_id || null,
    versionId: issue?.material_version_id || loc.material_version_id || loc.version_id || material?.current_version_id || null,
    page: Math.max(1, Number(loc.page_no) || 1),
  }
}

export function issueHighlights(issues, material, versionId) {
  if (!material) return []
  return issues.filter((issue) => {
    const loc = issueLocation(issue, material)
    return sameId(loc.materialId, material.id) && sameId(loc.versionId, versionId)
  }).map((issue) => ({ id: issue.id, ...issue.location, title: issue.title }))
}

export function batchReviewResult(selected, response) {
  const passed = new Set((response.passed || []).map(String))
  const failed = new Map((response.failed || []).map((failure) => [String(failure.submission_id), failure]))
  const remaining = selected.filter((id) => !passed.has(String(id)))
  return {
    passed: selected.length - remaining.length,
    remaining,
    failures: remaining.map((id) => failed.get(String(id)) || { submission_id: id, reason: "接口未返回处理结果，请刷新核实后重试" }),
  }
}

export function reviewHistoryLink(record, role) {
  if (!record.link_id) return null
  const id = encodeURIComponent(record.link_id)
  if (record.link_type === "material") return { to: `/materials/${id}`, label: "查看材料" }
  if (record.link_type === "submission") return { to: role === "STUDENT" ? `/my/self-check/${id}` : `/review/submissions/${id}`, label: "查看提交包" }
  if (record.link_type === "notice") return { to: role === "STUDENT" ? `/my/rectification?notice=${id}` : `/notices?notice=${id}`, label: "查看通知" }
  return null
}
