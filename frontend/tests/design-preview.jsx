// Development-only preview. Every request is handled in memory. No real token,
// localStorage credential, backend endpoint or student record is used.
import React from "react"
import { createRoot } from "react-dom/client"
import { createMemoryRouter, RouterProvider } from "react-router-dom"
import { api, tokenStore } from "../src/api/client"
import { AuthProvider } from "../src/context/AuthContext"
import { ToastProvider } from "../src/context/ToastContext"
import { appRoutes } from "../src/routes"
import { roleKey } from "../src/utils/identity"
import { FALLBACK_META } from "../src/utils/constants"
import "../src/index.css"

const options = new URLSearchParams(location.search)
const previewAccounts = [
  { username: "student", real_name: "示例学生", roles: [{ role: "STUDENT", org_id: 2 }] },
  { username: "admin", real_name: "示例管理员", roles: [{ role: "SYS_ADMIN", org_id: 1 }] },
  { username: "reviewer", real_name: "示例审核员", roles: [{ role: "BRANCH_REVIEWER", org_id: 2 }] },
  { username: "multi", real_name: "示例多身份账号", roles: [{ role: "STUDENT", org_id: 2, org_name: "示例学生党支部" }, { role: "BRANCH_REVIEWER", org_id: 3, org_name: "示例审核党支部" }] },
]
let account = null
let role = null
let student = false
const state = options.get("state") === "returned" ? "RETURNED" : options.get("state") === "review" ? "BRANCH_REVIEW" : "DRAFT"
const materialTypes = [{ id: 1, code: "THOUGHT_REPORT", name: "思想汇报" }, { id: 2, code: "APPLICATION", name: "入党申请书" }, { id: 3, code: "TRAINING", name: "培训结业证明" }]
const report = { id: 201, report_no: 2, status: "DONE", mode: "RULE_ONLY", is_stale: false, handover_status: "NOT_REQUIRED", recommendation: "NEEDS_REVIEW", summary: { total: 2, by_severity: { BLOCK: 1, WARN: 1 }, materials_checked: 2 }, rule_version: { version_no: 3 }, finished_at: "2026-10-19T09:20:00" }
const versions = [{ id: 401, version_no: 1, parse_status: "DONE", page_count: 2, file_size: 184210, uploaded_at: "2026-10-18T10:30:00", original_filename: "思想汇报.pdf" }]
const materials = [{ id: 12, title: "思想汇报.pdf", type_name: "思想汇报", current_version_id: 401, version_no: 1, open_issue_count: 2, current_version: versions[0], type_status: "CONFIRMED" }, { id: 13, title: "入党申请书.pdf", type_name: "入党申请书", current_version_id: 402, version_no: 1, current_version: { ...versions[0], id: 402 }, type_status: "CONFIRMED" }]
let issues = [{ id: 51, report_id: 201, material_id: 12, material_version_id: 401, category: "FORMAT", severity: "BLOCK", review_status: state === "RETURNED" ? "CONFIRMED" : "PENDING", is_active: true, title: "请核对本人签名", description: "自动检查未能确认手写签名，请结合材料原件核实。", suggestion: "核对落款签名；确有遗漏时，请补充签名后上传新版本。", rule_code: "FORMAT_SIGNATURE", rule_basis: "材料填写要求", location: { material_id: 12, page_no: 1, bbox: [55, 490, 500, 535], snippet: "请审核人员结合原件核对落款签名" } }, { id: 52, report_id: 201, material_id: 12, material_version_id: 401, category: "TIME", severity: "WARN", review_status: "PENDING", is_active: true, title: "材料日期需要核对", description: "当前填写日期与时间节点记录不一致，请确认实际日期。", suggestion: "对照时间轴记录核对日期，必要时校正记录。", location: { page_no: 1, bbox: [55, 190, 500, 230], snippet: "报告日期：2026年10月16日" } }]
let submission = { id: 101, stage_code: 2, stage_name: "入党积极分子", status: student ? state : "BRANCH_REVIEW", level: "BRANCH", round_no: 1, ai_status: "DONE", latest_report: report, archive: { id: 1, real_name: "示例同学", student_no: "20260001", branch_name: "示例学生党支部" }, materials, can: { submit: student && ["DRAFT", "RETURNED"].includes(state), self_check: student && ["DRAFT", "RETURNED"].includes(state), upload: student && ["DRAFT", "RETURNED"].includes(state), review: !student, add_issue: !student, edit_timeline: !student, ai_check: true, handover: false } }
const archive = { id: 1, real_name: "示例同学", student_no: "20260001", current_stage: 2, stage_name: "入党积极分子", status: "ACTIVE", branch_name: "示例学生党支部", current_submission: { id: 101, status: state, next_action: "请按清单准备材料" } }
const groups = [{ stage_code: 2, checklist: materialTypes.map((type, index) => ({ checklist_item_id: index + 1, material_type: type, required: true, expected_count: 1, actual_count: index < 2 ? 1 : 0, missing_count: index < 2 ? 0 : 1, materials: index < 2 ? [materials[index]] : [], requirement_text: index === 2 ? "上传培训结业证明的清晰扫描件。" : "请保证材料完整、文字清晰。" })), unclassified: [], extra: [] }]
const completeness = { is_complete: false, missing_total: 1, items: groups[0].checklist.map((item) => ({ ...item, expected: item.expected_count, actual: item.actual_count, missing: item.missing_count })) }
const names = ["示例同学", "示例同学二", "示例同学三", "示例同学四", "示例同学五", "示例同学六"]
const rows = names.map((name, index) => ({ id: 101 + index, student_name: name, student_no: `2026000${index + 1}`, branch_name: "示例学生党支部", stage_code: 2, stage_name: "入党积极分子", status: "BRANCH_REVIEW", ai_status: "DONE", recommendation: index === 2 ? "SUGGEST_PASS" : "NEEDS_REVIEW", handover_status: "NOT_REQUIRED", issue_counts: { BLOCK: index === 2 ? 0 : 1, WARN: index % 2 }, days_left: index + 1, submitted_at: "2026-10-18T10:30:00" }))
const timeline = { stages: [{ code: 1, status: "FILED" }, { code: 2, status: submission.status, submission_id: 101 }], nodes: [{ code: "N1", name: "递交入党申请", effective: { date: "2025-10-10" }, sources: [], locked: true }, { code: "N2", name: "确定为入党积极分子", effective: { date: "2026-04-12" }, sources: [{ material_id: 12, version_no: 1, page_no: 1, raw_text: "示例时间节点", date: "2026-04-12", bbox: [55, 190, 500, 230] }] }], derived: [] }
// Isolated memory store: preview login/logout never reads or changes real credentials.
const session = { access: "", refresh: "", role: "" }
for (const key of ["access", "refresh", "role"]) Object.defineProperty(tokenStore, key, { configurable: true, get: () => session[key] })
tokenStore.setRole = (value) => { session.role = value || "" }
tokenStore.clear = () => { session.access = ""; session.refresh = ""; session.role = "" }
globalThis.__previewRequests = []

function documentImage(page) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="595" height="842" viewBox="0 0 595 842"><rect width="595" height="842" fill="white"/><g font-family="Microsoft YaHei, sans-serif" fill="#283747"><text x="248" y="95" font-size="24">思想汇报</text><text x="55" y="150" font-size="14">姓名：示例同学　　学号：20260001</text><text x="55" y="212" font-size="14">报告日期：2026年10月16日</text><text x="55" y="268" font-size="14">本页面为界面设计预览使用的虚构材料。</text><text x="55" y="308" font-size="14">点击右侧问题，可定位原文中的相应位置。</text><text x="55" y="348" font-size="14">正式审核请以实际上传材料和人工核实结果为准。</text><text x="55" y="510" font-size="14">请审核人员结合原件核对落款签名。</text><text x="55" y="720" font-size="12" fill="#8b959f">界面预览 · 虚构数据 · 第 ${page} 页</text></g></svg>`
  return new Blob([svg], { type: "image/svg+xml" })
}

api.defaults.adapter = async (config) => {
  globalThis.__previewRequests.push({ method: config.method, url: config.url, data: config.data })
  const url = config.url
  let data
  if (url === "/auth/config") data = { mode: "demo" }
  else if (url === "/auth/demo-accounts") data = previewAccounts.map((item) => ({ ...item, password_hint: "Preview123!" }))
  else if (url === "/auth/login") {
    const body = JSON.parse(config.data)
    account = previewAccounts.find((item) => item.username === body.username && body.password === "Preview123!")
    if (!account) throw new Error("演示账号或密码错误，请展开下方演示账号选择。")
    data = { access_token: "preview-only", refresh_token: "preview-refresh", user: account, must_change_password: false }
  }
  else if (url === "/auth/me") {
    if (!account) throw new Error("请先登录演示账号")
    role = account.roles.find((item) => roleKey(item) === config.headers["X-Active-Role"]) || account.roles[0]
    student = role.role === "STUDENT"
    submission = { ...submission, status: student ? state : "BRANCH_REVIEW", can: { submit: student && ["DRAFT", "RETURNED"].includes(state), self_check: student && ["DRAFT", "RETURNED"].includes(state), upload: student && ["DRAFT", "RETURNED"].includes(state), review: role.role === "BRANCH_REVIEWER", add_issue: !student, edit_timeline: !student, ai_check: true, handover: false } }
    data = { ...account, id: 1, org_name: "示例学院", active_role: role, must_change_password: false }
  }
  else if (url === "/meta") data = { ...FALLBACK_META, material_types: materialTypes }
  else if (url === "/messages/unread-count") data = { count: 2 }
  else if (url === "/dashboard") data = student ? { role: "STUDENT", archive_id: 1, current_stage: 2, stage_name: "入党积极分子", submission: { id: 101, status: state }, open_issues: { BLOCK: 1, WARN: 1 }, timeline_preview: [{ code: "递交申请", date: "2025-10-10" }, { code: "确定为积极分子", date: "2026-04-12" }] } : { role: role.role, todo: { to_review: 6, returned_waiting: 2, due_soon: 3, pending_ai: 0 }, deadlines: rows.slice(0, 3).map((row) => ({ submission_id: row.id, student_name: row.student_name, days_left: row.days_left, deadline: `2026-10-${20 + row.id - 101}` })), issue_distribution: { FORMAT: 3, TIME: 2 }, progress: { by_stage: [{ stage_code: 2, BRANCH_REVIEW: 6, RETURNED: 2, FILED: 4 }] }, batch: { id: 1, name: "2026 年秋季发展批次" } }
  else if (url === "/my/archive" || url === "/archives/1") data = archive
  else if (url === "/archives/1/timeline") data = timeline
  else if (url === "/archives/1/history" || url.endsWith("/review-records")) data = []
  else if (url === "/archives/1/materials") data = groups
  else if (url === "/submissions") {
    const filtered = rows.filter((row) => !config.params?.q || row.student_name.includes(config.params.q) || row.student_no.includes(config.params.q))
    data = { items: filtered, total: filtered.length, page: 1, page_size: 20 }
  }
  else if (/^\/submissions\/\d+$/.test(url)) data = submission
  else if (url.endsWith("/completeness")) data = completeness
  else if (url.endsWith("/issues")) data = { items: issues, counts: {} }
  else if (/^\/issues\/\d+$/.test(url) && config.method === "put") { const body = JSON.parse(config.data); const issue = issues.find((item) => item.id === Number(url.split("/").pop())); issue.review_status = ({ confirm: "CONFIRMED", reject: "REJECTED", reset: "PENDING", modify: "MODIFIED" })[body.action]; issue.review_note = body.note; data = issue }
  else if (url.startsWith("/reports/")) data = report
  else if (/^\/materials\/\d+\/pages\/\d+$/.test(url)) data = documentImage(url.split("/").pop())
  else if (/^\/materials\/\d+\/versions$/.test(url)) data = versions
  else if (url === "/notices") data = { items: [] }
  else if (url === "/archives") data = { items: [archive], total: 1, page: 1, page_size: 20 }
  else if (url === "/batches") data = { items: [{ id: 1, name: "示例批次" }] }
  else if (url === "/users" && config.method === "get") data = { items: previewAccounts.map((item, index) => ({ ...item, id: index + 1, is_active: true, org_name: "示例学院" })), total: previewAccounts.length, page: 1, page_size: 20 }
  else if (url === "/orgs" && config.method === "get") data = [{ id: 1, name: "示例大学", org_type: "SCHOOL", is_active: true, children: [{ id: 2, name: "示例学院", org_type: "COLLEGE", is_active: true, children: [{ id: 3, name: "示例学生党支部", org_type: "BRANCH", is_active: true }] }] }]
  else if (url === "/settings" && config.method === "get") data = { ai: { enabled: false }, storage: {}, security: {} }
  else if (url === "/audit-logs") data = { items: [], total: 0, page: 1, page_size: 20 }
  else if (url.endsWith("/review")) { data = { notice_id: 601 }; submission = { ...submission, status: "RETURNED", can: {} } }
  else if (url === "/auth/logout") data = {}
  else throw new Error("此预览仅展示主要办理页面，请在正式服务中使用此功能。")
  return { config, status: 200, statusText: "OK", headers: { "x-page-count": "2", "x-page-width": "595", "x-page-height": "842" }, data: config.responseType === "blob" ? data : { code: 0, message: "ok", data } }
}

const router = createMemoryRouter(appRoutes, { initialEntries: ["/login"] })
globalThis.__previewNavigate = (path) => router.navigate(path)
createRoot(document.getElementById("root")).render(<ToastProvider><AuthProvider><div style={{ padding: "7px 16px", background: "#fff8df", color: "#735913", fontSize: 12 }}>界面预览 · 虚构数据，不连接服务器。登录页可展开演示账号；退出登录后可体验其他身份。</div><RouterProvider router={router} /></AuthProvider></ToastProvider>)
