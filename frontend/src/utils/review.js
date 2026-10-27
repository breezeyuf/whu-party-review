export const sameId = (a, b) => a != null && b != null && String(a) === String(b)

// 通过规则的统一说明：单份通过、批量通过与备案共用后端同一个校验（services/workflow.ensure_passable）
export const PASS_RULE_TEXT = "仍有待处理的阻断问题时不能通过；已确认、修改或驳回的阻断问题不拦截，单份与批量一致。"

// 待办的筛选、计数和分页全部由 GET /api/submissions 完成；这里只去掉空值，其余参数
// （含 has_block=false、due_within_days）原样交给后端，取值是否合法也由后端判断（422）
export function reviewTaskQuery(query = {}) {
  return Object.fromEntries(Object.entries(query).filter(([, value]) => value != null && value !== ""))
}

// 每次查询只发一个列表请求，列表、总数和页码都取服务端结果
export async function loadReviewTasks(fetchPage, query) {
  return fetchPage(reviewTaskQuery(query))
}

const QUERY_FIELD_NAME = { due_within_days: "截止天数", has_block: "阻断问题", stage_code: "阶段", batch_id: "批次", branch_id: "支部", min_issues: "问题数", todo: "任务范围" }

// 后端参数校验失败（422）时指出是哪个筛选条件，其他错误原样显示
export function reviewQueryErrorText(error) {
  const fields = (error?.data?.errors || []).map((item) => item?.loc?.[item.loc.length - 1]).filter(Boolean)
  if (error?.status !== 422 || !fields.length) return error?.message
  const names = [...new Set(fields)].map((field) => QUERY_FIELD_NAME[field] || field).join("、")
  return `${error.message || "参数校验失败"}：${names}的取值无效，请调整或清除筛选条件。`
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
  if (record.link_type === "material") return { to: `/materials/${id}${record.version_id ? `?version_id=${encodeURIComponent(record.version_id)}` : ""}`, label: "查看材料" }
  if (record.link_type === "submission") {
    // AI 报告事件带 report_id：直接打开当时那份报告，而不是当前最新报告
    const query = record.report_id ? `?report=${encodeURIComponent(record.report_id)}` : ""
    return {
      to: `${role === "STUDENT" ? `/my/self-check/${id}` : `/review/submissions/${id}`}${query}`,
      label: record.report_id ? "查看当时报告" : "查看提交包",
    }
  }
  if (record.link_type === "notice") return { to: role === "STUDENT" ? `/my/rectification?notice=${id}` : `/notices?notice=${id}`, label: "查看通知" }
  if (record.link_type === "archive") return { to: role === "STUDENT" ? "/my/progress" : `/archives/${id}`, label: "查看时间节点" }
  return null
}
