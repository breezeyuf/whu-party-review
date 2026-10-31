import React, { act } from "react"
import { createRoot } from "react-dom/client"
import { createMemoryRouter, RouterProvider } from "react-router-dom"
import assert from "node:assert/strict"
import { api, tokenStore } from "../src/api/client"
import { AuthProvider } from "../src/context/AuthContext"
import { ToastProvider } from "../src/context/ToastContext"
import ArchiveListPage from "../src/pages/archive/ArchiveListPage"
import UsersPage from "../src/pages/admin/UsersPage"
import OrgsPage from "../src/pages/admin/OrgsPage"
import SettingsPage from "../src/pages/admin/SettingsPage"
import BatchesPage from "../src/pages/admin/BatchesPage"
import ExportPage from "../src/pages/stats/ExportPage"
import MessagesPage from "../src/pages/MessagesPage"
import NoticesPage from "../src/pages/notice/NoticesPage"
import ArchiveDetailPage from "../src/pages/archive/ArchiveDetailPage"
import SelfCheckPage from "../src/pages/student/SelfCheckPage"
import RectificationPage from "../src/pages/student/RectificationPage"
import MyMaterialsPage from "../src/pages/student/MyMaterialsPage"
import MyProgressPage from "../src/pages/student/MyProgressPage"
import MaterialDetailPage from "../src/pages/material/MaterialDetailPage"
import BatchUploadPage from "../src/pages/material/BatchUploadPage"
import ReviewDecisionPanel from "../src/components/review/ReviewDecisionPanel"
import IssueActions from "../src/components/review/IssueActions"
import FileUploader from "../src/components/common/FileUploader"
import MaterialViewer from "../src/components/material/MaterialViewer"
import ParsedTextPanel from "../src/components/material/ParsedTextPanel"
import AddIssueModal from "../src/components/review/AddIssueModal"
import ReviewWorkspacePage from "../src/pages/review/ReviewWorkspacePage"
import IssueResponseForm from "../src/components/student/IssueResponseForm"
import ReviewJobStatus from "../src/components/review/ReviewJobStatus"
import { StudentDashboard, ReviewerDashboard, AdminDashboard } from "../src/pages/dashboard/Dashboards"
import AppLayout from "../src/components/layout/AppLayout"
import RuleSectionLayout from "../src/components/rules/RuleSectionLayout"
import FilterBar from "../src/components/common/FilterBar"
import ReviewTasksPage from "../src/pages/review/ReviewTasksPage"
import CrossReviewConfigPage from "../src/pages/review/CrossReviewConfigPage"
import AuditLogsPage from "../src/pages/admin/AuditLogsPage"
import JobsPage from "../src/pages/review/JobsPage"
import RouteError from "../src/components/common/RouteError"
import { lazyWithRetry } from "../src/utils/lazyLoad"
import { pages as shellPages } from "../src/components/layout/shellModule"
import { shellPageNames } from "../src/components/layout/lazyShell"
import AiQualityPage from "../src/pages/stats/AiQualityPage"
import ReportSummary from "../src/components/review/ReportSummary"
import "../src/routes"
import CompleteSettingsPage from "../src/pages/admin/CompleteSettingsPage"
import RuleVersionsPage from "../src/pages/rules/RuleVersionsPage"
import ContentTabs from "../src/components/common/ContentTabs"
import ActionPopover from "../src/components/common/ActionPopover"
import IssueCard from "../src/components/review/IssueCard"
import NoticePreview from "../src/components/notice/NoticePreview"
import ChecklistsPage from "../src/pages/rules/ChecklistsPage"
import TimelineView from "../src/components/archive/TimelineView"

const wait = (ms = 15) => new Promise((resolve) => setTimeout(resolve, ms))
const flush = () => act(async () => { await wait(); await wait() })
const baseReport = { id: 201, status: "DONE", is_stale: false, summary: {}, handover_status: "NOT_REQUIRED", recommendation: "PASS" }
const baseArchive = { id: 1, real_name: "测试学生", student_no: "20260001", branch_id: 2, batch_id: 1, current_stage: 1, status: "ACTIVE", submissions: [], current_submission: { id: 101, status: "DRAFT" } }
const baseSubmission = { id: 101, archive: { id: 1, real_name: "测试学生" }, stage_code: 1, stage_name: "申请入党", status: "DRAFT", ai_status: "DONE", latest_report: baseReport, can: { self_check: true, submit: true } }
const complete = { is_complete: true, missing_total: 0, items: [{ material_type: { id: 1, name: "申请书" }, required: true, expected: 1, actual: 1, missing: 0 }] }
const groups = [{ stage_code: 1, checklist: [], unclassified: [], extra: [] }]
const oldVersion = { id: 401, version_no: 1, parse_status: "DONE", file_size: 100, page_count: 3 }
const currentVersion = { id: 402, version_no: 2, parse_status: "DONE", file_size: 120, page_count: 3, is_current: true }
const baseMaterial = { id: 12, archive_id: 1, submission_id: 101, title: "思想汇报.pdf", editable: true, current_version: currentVersion, type: { id: 1, name: "思想汇报" }, type_status: "CONFIRMED" }
const nodeDefinitions = [{ code: "T02", name: "申请日期", value_kind: "DATE", is_active: true }, { code: "T06", name: "思想汇报日期", value_kind: "DATE_SEQ", is_active: true }, { code: "T10", name: "集中培训", value_kind: "DATE_RANGE", has_hours: true, is_active: true }]

let root, router, requests, fixture, role
const text = () => document.getElementById("root").textContent
const button = (label) => [...document.querySelectorAll("button")].find((node) => node.textContent.trim() === label)
const click = async (node) => {
  assert.ok(node, "未找到按钮")
  await act(async () => { node.click(); await wait() })
  await flush()
}
const input = async (node, value) => {
  assert.ok(node, "未找到输入框")
  await act(async () => {
    const proto = node.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : node.tagName === "SELECT" ? HTMLSelectElement.prototype : HTMLInputElement.prototype
    Object.getOwnPropertyDescriptor(proto, "value").set.call(node, value)
    node.dispatchEvent(new Event(node.tagName === "SELECT" ? "change" : "input", { bubbles: true }))
    await wait()
  })
}

function defaultFixture(config) {
  const url = config.url
  if (url === "/auth/me") return { id: 1, real_name: "测试用户", active_role: role, roles: [role], must_change_password: false }
  if (url === "/my/archive") return baseArchive
  if (url === "/submissions/101") return baseSubmission
  if (url === "/submissions/101/completeness") return complete
  if (url === "/submissions/101/issues") return { items: [], counts: {} }
  if (url === "/submissions/101/review-records") return []
  if (url === "/reports/201") return baseReport
  if (url === "/archives/1/materials") return groups
  if (url === "/archives/1") return baseArchive
  if (url === "/archives/1/timeline") return { stages: [], nodes: [], derived: [], report_is_stale: false }
  if (url === "/archives/1/history") return []
  if (url === "/materials/12") return baseMaterial
  if (url === "/materials/12/versions") return [oldVersion, currentVersion]
  if (url === "/materials/12/parsed") return { version_id: config.params?.version_id, full_text: "测试解析文本", extracted_fields: {}, extractions: [], page_count: 3 }
  if (url === "/materials/12/diff") return { from: oldVersion, to: currentVersion, stats: { added: 1 }, hunks: [{ op: "insert", from_text: "", to_text: "测试新增文字" }] }
  if (/^\/materials\/\d+\/pages\/\d+$/.test(url)) return new Blob(["test image"], { type: "image/png" })
  if (url === "/archives") return { items: [{ ...baseArchive, submission: { id: 101, status: "DRAFT" } }], total: 1, page: 1, page_size: 20 }
  if (url === "/batches") return { items: [{ id: 1, name: "测试批次" }] }
  if (url === "/orgs") return [{ id: 2, org_type: "BRANCH", parent_id: 1, name: "测试支部" }]
  if (url === "/notices") return { items: [] }
  if (url === "/meta") return { time_nodes: nodeDefinitions }
  if (url === "/messages/unread-count") return { count: 0 }
  if (url === "/submissions") return { items: [{ id: 101, student_name: "测试学生", stage_code: 1, status: "BRANCH_REVIEW", issue_counts: {} }], total: 1, page: 1, page_size: 20 }
  throw new Error(`测试缺少接口样例：${config.method} ${url}`)
}

async function mount(element, { path = "/", pattern = path.split("?")[0], roleCode = "STUDENT", handler, routes } = {}) {
  if (root) await act(async () => root.unmount())
  router?.dispose()
  document.getElementById("root").innerHTML = ""
  role = { role: roleCode, org_id: roleCode === "BRANCH_REVIEWER" ? 2 : 1 }
  requests = []
  fixture = handler
  tokenStore.setTokens("isolated-test-token", "isolated-test-refresh")
  tokenStore.setRole(`${role.role}@${role.org_id}`)
  api.defaults.adapter = async (config) => {
    requests.push({ ...config, data: config.data })
    let data = fixture ? await fixture(config) : undefined
    if (data === undefined) data = defaultFixture(config)
    return { config, status: 200, statusText: "OK", headers: { "x-page-count": "3", "x-page-width": "595", "x-page-height": "842" }, data: config.responseType === "blob" ? data : { code: 0, message: "ok", data } }
  }
  router = createMemoryRouter(routes || [{ path: pattern, element }], { initialEntries: [path] })
  root = createRoot(document.getElementById("root"))
  await act(async () => root.render(<ToastProvider><AuthProvider><RouterProvider router={router} /></AuthProvider></ToastProvider>))
  await flush()
}

export async function runUiScenarios() {
  const results = []
  const test = async (name, run) => {
    try { await run(); results.push({ name, passed: true }) }
    catch (error) { results.push({ name, passed: false, error: error.stack || error.message }) }
  }

  await test("系统管理员首页四个入口真实可见，组织部首页优先备案且不越权", async () => {
    await mount(<AdminDashboard data={{ role: "SYS_ADMIN" }} />, { roleCode: "SYS_ADMIN" })
    for (const path of ["/admin/users", "/admin/orgs", "/admin/settings", "/admin/audit-logs"]) assert.ok(document.querySelector(`[aria-label="管理功能"] a[href="${path}"]`))
    assert.equal(document.querySelector('a[href="/review/tasks"]'), null)
    await mount(<AdminDashboard data={{ role: "ORG_ADMIN", todo: { to_review: 6 } }} />, { roleCode: "ORG_ADMIN" })
    assert.match(document.querySelector(".next-action").textContent, /6 份材料等待备案/)
    assert.equal(document.querySelector(".next-action .btn-primary").getAttribute("href"), "/review/tasks")
    assert.ok(document.querySelector('a[href="/admin/batches"]'))
  })

  await test("配置分类切换与保存失败均保留草稿和密钥输入", async () => {
    await mount(<CompleteSettingsPage />, { path: "/admin/settings", roleCode: "SYS_ADMIN", handler: c => {
      if (c.url === "/settings" && c.method === "get") return { ai: { model: "old" }, upload: {}, ocr: {} }
      if (c.url === "/settings" && c.method === "put") throw Error("保存失败测试")
    } })
    assert.equal(document.getElementById("settings-ai").hidden, false)
    assert.equal(document.getElementById("settings-upload").hidden, true)
    await input(document.querySelector('[aria-label="模型名"]'), "draft-model")
    await input(document.querySelector('[aria-label="API 密钥"]'), "fictional-key")
    await click(button("材料与业务"))
    assert.equal(document.getElementById("settings-ai").hidden, true)
    await click(button("模型与识别"))
    assert.equal(document.querySelector('[aria-label="模型名"]').value, "draft-model")
    assert.equal(document.querySelector('[aria-label="API 密钥"]').value, "fictional-key")
    await click(button("保存大模型"))
    assert.match(text(), /保存失败测试/)
    assert.equal(document.querySelector('[aria-label="模型名"]').value, "draft-model")
    assert.equal(requests.filter(c => c.url.includes("/test")).length, 0)
  })

  await test("组织部默认业务配置，技术配置只读，旧锚点仍可定位", async () => {
    const handler = c => c.url === "/settings" ? { ai: { model: "model-name" }, worker: { concurrency: 2 }, upload: {} } : undefined
    await mount(<CompleteSettingsPage />, { path: "/admin/settings", roleCode: "ORG_ADMIN", handler })
    assert.equal(document.getElementById("settings-upload").hidden, false)
    assert.equal(document.getElementById("settings-ai").hidden, true)
    await click(button("技术配置（只读）"))
    assert.equal(document.getElementById("settings-ai").hidden, false)
    assert.equal(document.querySelector('[aria-label="模型名"]'), null)
    assert.match(document.getElementById("settings-ai").textContent, /model-name/)
    assert.equal(button("保存大模型"), undefined)
    await mount(<CompleteSettingsPage />, { path: "/admin/settings#settings-worker", pattern: "/admin/settings", roleCode: "SYS_ADMIN", handler })
    assert.equal(document.getElementById("settings-worker").hidden, false)
    await click(button("模型与识别"))
    assert.equal(router.state.location.hash, "")
    assert.equal(document.getElementById("settings-worker").hidden, true)
  })

  await test("用户导入默认收起，可显式展开而不发起导入请求", async () => {
    await mount(<UsersPage />, { roleCode: "SYS_ADMIN" })
    assert.equal(document.getElementById("user-import-panel").hidden, true)
    await click(button("批量导入"))
    assert.equal(document.getElementById("user-import-panel").hidden, false)
    await click(button("批量导入"))
    assert.equal(document.getElementById("user-import-panel").hidden, true)
    assert.equal(requests.some(c => c.method === "post"), false)
  })

  await test("学生识别JSON默认收起，审核人员字段校正仍直接可见", async () => {
    const parsed = { full_text: "虚构材料", extracted_fields: { name: "样例" }, extractions: [] }
    await mount(<ParsedTextPanel parsed={parsed} editable={false} />)
    const detail = [...document.querySelectorAll("details")].find(d => d.querySelector("summary")?.textContent === "识别详情")
    assert.equal(detail.open, false)
    assert.equal(button("保存校正"), undefined)
    await mount(<ParsedTextPanel parsed={parsed} editable onSave={() => {}} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal([...document.querySelectorAll("details")].find(d => d.querySelector("summary")?.textContent === "抽取字段校正").open, true)
  })

  await test("报告技术信息收起，规则模式和过期风险保持可见", async () => {
    await mount(<ReportSummary report={{ ...baseReport, report_no: 5, mode: "RULE_ONLY", is_stale: true }} />)
    assert.match(text(), /仅规则（未使用大模型）/)
    assert.match(text(), /报告已过期/)
    const details = [...document.querySelectorAll("details")].find(d => d.querySelector("summary")?.textContent === "报告详情")
    assert.equal(details.open, false)
    assert.match(details.textContent, /报告 #5/)
  })

  await test("AI成效零样本不呈现准确率，核验数据出现后展示真实比例", async () => {
    await mount(<AiQualityPage />, { roleCode: "SYS_ADMIN", handler: c => c.url === "/stats/ai-quality" ? { reviewed: 0, confirm_rate: 0, false_positive_rate: 0 } : undefined })
    assert.match(text(), /暂无人工核验样本/)
    const metrics = document.querySelector(".stats")
    assert.doesNotMatch(metrics.textContent, /0%/)
    assert.equal([...document.querySelectorAll("details")].find(d => d.querySelector("summary")?.textContent === "详细分类与规则分析").open, false)
    await mount(<AiQualityPage />, { roleCode: "SYS_ADMIN", handler: c => c.url === "/stats/ai-quality" ? { reviewed: 10, confirm_rate: 0.8, false_positive_rate: 0.2 } : undefined })
    assert.match(document.querySelector(".stats").textContent, /80%/)
    assert.match(document.querySelector(".stats").textContent, /20%/)
  })

  await test("两类管理员首页去掉辅助工具和规则维护块，菜单功能仍保留", async () => {
    for (const role of ["SYS_ADMIN", "ORG_ADMIN"]) {
      await mount(<AdminDashboard data={{ role, todo: { to_review: 2 } }} />, { roleCode: role })
      assert.equal(document.querySelector('[aria-label="辅助工具"]'), null)
      assert.equal(document.querySelector('[aria-label="规则与维护"]'), null)
      assert.ok(document.querySelector('[aria-label="管理功能"], [aria-label="日常办理"]'))
    }
  })

  await test("删除最后一份自传后补充入口保留，重新上传携带原类型与阶段", async () => {
    let removed = false, uploaded = false
    await mount(<MyMaterialsPage />, { path: "/my/materials", handler: c => {
      if (c.url === "/my/archive") return { ...baseArchive, current_stage: 3 }
      if (c.url === "/meta") return { material_types: [{ id: 9, name: "自传", stage_codes: [3] }] }
      if (c.url === "/materials/12" && c.method === "delete") { removed = true; return {} }
      if (c.url === "/archives/1/materials" && c.method === "post") { uploaded = true; return { material: { id: 13 } } }
      if (c.url === "/archives/1/materials") return [{ stage_code: 3, checklist: [], unclassified: [], extra: removed ? [] : [{ id: 12, title: "测试自传.jpg", current_version: { parse_status: "DONE" } }] }]
    } })
    await click(button("删除")); await click(button("确认删除"))
    assert.equal(removed, true)
    assert.ok(button("上传补充材料"))
    await input(document.querySelector('[aria-label="补充材料类型"]'), "9")
    const file = document.querySelector('[aria-label="补充材料上传"] input[type="file"]')
    Object.defineProperty(file, "files", { configurable: true, value: [new File(["synthetic"], "重新上传自传.jpg", { type: "image/jpeg" })] })
    await act(async () => { file.dispatchEvent(new Event("change", { bubbles: true })); await wait() })
    await flush()
    assert.equal(uploaded, true)
    const request = requests.find(c => c.method === "post" && c.url === "/archives/1/materials")
    assert.equal(request.data.get("material_type_id"), "9")
    assert.equal(request.data.get("stage_code"), "3")
    assert.equal(requests.some(c => c.method === "delete" && c.url !== "/materials/12"), false)
  })

  await test("消息分页可选每页条数，切换筛选回第一页且标题使用固定列对齐", async () => {
    await mount(<MessagesPage />, { path: "/messages?page=3", pattern: "/messages", handler: c => {
      if (c.url === "/messages") return { items: [{ id: 1, title: "需要换行的较长消息标题，用于检验文字与图标对齐", is_read: false, content: "测试内容" }, { id: 2, title: "已读标题", is_read: true }], total: 65, page: c.params.page, page_size: c.params.page_size }
    } })
    const pager = document.querySelector('[aria-label="每页显示条数"]')
    assert.ok(pager)
    assert.deepEqual([...pager.options].map(o => o.value), ["10", "20", "50", "100"])
    await input(pager, "50")
    assert.equal(requests.filter(c => c.url === "/messages").at(-1).params.page_size, 50)
    assert.equal(requests.filter(c => c.url === "/messages").at(-1).params.page, 1)
    await click(button("下一页")); await click(button("未读"))
    const last = requests.filter(c => c.url === "/messages").at(-1)
    assert.equal(last.params.page, 1); assert.equal(last.params.is_read, "false")
    assert.ok([...document.querySelectorAll("td button")].every(b => b.className.includes("grid-cols-") && !b.querySelector("svg")))
    assert.equal(document.querySelectorAll("[data-message-title]").length, 2)
    assert.ok([...document.querySelectorAll("[data-message-title]")].every(n => n.closest("td").cellIndex === 1))
  })

  await test("各阶段清单共用六列宽度，只读时保留操作列但不提供编辑", async () => {
    const handler=c=>c.url==="/rules/checklists"?[1,2].map(n=>({stage_code:n,items:[{id:n,material_type:{name:n===1?"申请书":"长名称的培养考察材料"},quantity_mode:"FIXED",fixed_count:1,is_required:true}]})):c.url==="/rules/material-types"?{items:[]}:undefined
    await mount(<ChecklistsPage/>,{roleCode:"ORG_ADMIN",handler})
    const tables=[...document.querySelectorAll("table")]
    assert.equal(tables.length,2)
    assert.deepEqual([...tables[0].querySelectorAll("col")].map(c=>c.style.width),["24%","14%","8%","7%","35%","12%"])
    assert.deepEqual([...tables[1].querySelectorAll("col")].map(c=>c.style.width),[...tables[0].querySelectorAll("col")].map(c=>c.style.width))
    await mount(<ChecklistsPage/>,{roleCode:"BRANCH_REVIEWER",handler})
    assert.equal(button("编辑"),undefined)
    assert.equal(document.querySelectorAll("thead th").length,12)
    assert.match(text(),/只读/)
  })

  await test("备案内容直接切换五项，切换不丢驳回草稿", async () => {
    await mount(<ReviewWorkspacePage/>,{path:"/review/submissions/101",pattern:"/review/submissions/:id",roleCode:"ORG_ADMIN",handler:c=>{
      if(c.url==="/submissions/101")return {...baseSubmission,status:"ORG_FILING",level:"ORG",materials:[{id:12,current_version_id:402,title:"材料"}],can:{add_issue:true,file:true,review:true}}
      if(c.url==="/submissions/101/issues")return {items:[{id:71,title:"需核实的关键问题",severity:"BLOCK",category:"FORMAT",review_status:"PENDING",material_id:12}]}
    }})
    const tabs=[...document.querySelectorAll('[aria-label="工作区内容"] [role="tab"]')]
    assert.deepEqual(tabs.map(t=>t.textContent),["问题清单","材料完整性","时间节点","自查报告","审核记录"])
    await click(button("驳回误报"));await input(document.querySelector('[aria-label="驳回理由"]'),"核对原图后的草稿理由")
    await click(button("自查报告"));await click(button("问题清单"))
    assert.equal(document.querySelector('[aria-label="驳回理由"]').value,"核对原图后的草稿理由")
    assert.equal(document.querySelector('.service-more-actions'),null)
    assert.equal(document.querySelector('.review-stage-links'),null)
    assert.equal(requests.some(r=>r.method==="put"||r.method==="post"),false)
  })

  await test("更多操作支持Esc与外部关闭并返回触发按钮", async () => {
    let selected=0
    await mount(<ActionPopover><button onClick={()=>selected++}>示例操作</button></ActionPopover>)
    await click(button("更多操作"));assert.ok(button("示例操作"))
    await act(async()=>document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true})))
    assert.equal(button("示例操作"),undefined);assert.equal(document.activeElement,button("更多操作"))
    await click(button("更多操作"));await act(async()=>document.body.dispatchEvent(new MouseEvent("pointerdown",{bubbles:true})))
    assert.equal(button("示例操作"),undefined)
    await click(button("更多操作"));await click(button("示例操作"));assert.equal(selected,1)
  })

  await test("原文依据无三角文案，可展开且不会误选问题；旧通知等级兼容", async () => {
    let chosen=0
    await mount(<IssueCard issue={{id:1,title:"缺材料",severity:"BLOCK",rule_basis:"核实原件"}} onSelect={()=>chosen++}/>)
    const summary=document.querySelector("summary")
    assert.equal(summary.textContent,"查看依据");await click(summary)
    assert.equal(document.querySelector("details").open,true);assert.equal(chosen,0)
    assert.doesNotMatch(text(),/选中问题|阻断/)
    await mount(<NoticePreview notice={{title:"历史通知",content:{items:[{no:1,severity:"阻断",problem:"历史正文保持"}]}}}/>)
    assert.match(text(),/关键问题/);assert.match(text(),/历史正文保持/)
  })

  await test("共享标签支持方向键与Home/End键切换和焦点管理", async () => {
    function Harness(){const [value,setValue]=React.useState("a");return <ContentTabs items={[["a","第一页"],["b","第二页"],["c","第三页"]]} value={value} onChange={setValue} label="内容切换" idPrefix="test-tabs"/>}
    await mount(<Harness/>)
    const first=button("第一页")
    await act(async()=>first.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowRight",bubbles:true})))
    assert.equal(document.activeElement,button("第二页"));assert.equal(button("第二页").getAttribute("aria-selected"),"true")
    await act(async()=>button("第二页").dispatchEvent(new KeyboardEvent("keydown",{key:"End",bubbles:true})))
    assert.equal(document.activeElement,button("第三页"))
    await act(async()=>button("第三页").dispatchEvent(new KeyboardEvent("keydown",{key:"Home",bubbles:true})))
    assert.equal(document.activeElement,button("第一页"))
  })

  await test("审核员切换材料详情标签保留未保存的解析校正", async () => {
    await mount(<MaterialDetailPage/>,{path:"/materials/12",pattern:"/materials/:id",roleCode:"BRANCH_REVIEWER",handler:c=>c.url==="/submissions/101"?{...baseSubmission,can:{review:true}}:undefined})
    await click(button("解析文本"))
    const field=document.querySelector('#material-tabs-panel-text textarea')
    assert.equal(field.readOnly,false)
    await input(field,"尚未保存的校正草稿")
    await click(button("版本"));await click(button("解析文本"))
    assert.equal(document.querySelector('#material-tabs-panel-text textarea').value,"尚未保存的校正草稿")
    assert.equal(requests.some(r=>r.method==="put"),false)
  })

  await test("任务默认按人折叠，展开精确筛选且组内分页独立", async () => {
    await mount(<JobsPage />, { path: "/tasks/jobs", roleCode: "SYS_ADMIN", handler: (c) => {
      if (c.url === "/jobs/creators") return { items: [{ created_by: 17, name: "测试发起人", username: "same-name-a", total: 25, running: 1, failed: 2 }], total: 1, page: 1, page_size: 10 }
      if (c.url === "/jobs") return { items: [{id: 70, job_type: "NOTICE_BATCH", status: "SUCCEEDED", total:1}], total:25, page:c.params.page, page_size:c.params.page_size }
    } })
    assert.equal(requests.filter((c) => c.url === "/jobs").length, 0)
    await click([...document.querySelectorAll("button")].find((b) => b.textContent.includes("测试发起人")))
    assert.match(text(), /批量补全通知/)
    let last = requests.filter((c) => c.url === "/jobs").at(-1)
    assert.equal(last.params.created_by, 17)
    assert.equal(last.params.page_size, 20)
    await click([...document.querySelectorAll("button")].find((b) => b.textContent === "下一页" && !b.disabled))
    last = requests.filter((c) => c.url === "/jobs").at(-1)
    assert.equal(last.params.page, 2)
    assert.equal(requests.filter((c) => c.url === "/jobs/creators").length, 1)
    await input(document.querySelector('input[placeholder="姓名或账号"]'), "someone")
    assert.equal([...document.querySelectorAll("button")].find((b) => b.textContent.includes("测试发起人")).getAttribute("aria-expanded"), "false")
  })

  await test("日志搜索选择操作人使用精确ID，清除后保留时间列表", async () => {
    await mount(<AuditLogsPage />, { path: "/admin/audit-logs", roleCode: "SYS_ADMIN", handler: (c) => {
      if (c.url === "/audit-logs/actors") return { items: [{key:"17",user_id:17,username:"actor-a",name:"同名操作人"},{key:"18",user_id:18,username:"actor-b",name:"同名操作人"}], total:2 }
      if (c.url === "/audit-logs") return { items:[],total:0 }
    } })
    await click(button("选择操作人"))
    await input(document.querySelector('[aria-label="搜索操作人姓名或账号"]'), "同名")
    await click([...document.querySelectorAll("button")].find((b) => b.textContent.includes("actor-b")))
    assert.equal(requests.filter((c) => c.url === "/audit-logs").at(-1).params.user_id, "18")
    await click(button("清除操作人"))
    assert.equal(requests.filter((c) => c.url === "/audit-logs").at(-1).params.user_id, undefined)
  })

  await test("消息悬停仅展示，全部已读成功刷新红点且Esc可关闭", async () => {
    let unread = 3
    await mount(<AppLayout><p>测试首页</p></AppLayout>, {roleCode:"SYS_ADMIN",handler:(c) => {
      if(c.url === "/messages/unread-count") return {count:unread}
      if(c.url === "/messages/read-all") {unread=0;return {updated:3}}
    }})
    const messageButton=document.querySelector('[aria-label="消息，3 条未读"]')
    await act(async () => {messageButton.dispatchEvent(new MouseEvent("mouseover",{bubbles:true}));await wait()})
    assert.ok(button("全部标为已读"))
    assert.equal(requests.filter((c) => c.url === "/messages/read-all").length,0)
    await click(button("全部标为已读"))
    assert.ok(document.querySelector('[aria-label="消息"]'))
    assert.equal(button("全部标为已读").disabled,true)
    await act(async()=>{document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));await wait()})
    assert.equal(button("全部标为已读"),undefined)
    await click(document.querySelector('[aria-label="展开消息快捷操作"]'))
    assert.ok(button("查看消息"))
  })

  await test("消息标记期间重复点击只发送一次请求", async () => {
    let finish
    await mount(<AppLayout><p>测试首页</p></AppLayout>, {roleCode:"SYS_ADMIN",handler:(c) => {
      if(c.url === "/messages/unread-count") return {count:2}
      if(c.url === "/messages/read-all") return new Promise((resolve)=>{finish=resolve})
    }})
    await click(document.querySelector('[aria-label="展开消息快捷操作"]'))
    await click(button("全部标为已读"))
    assert.equal(button("正在标记…").disabled,true)
    await click(button("正在标记…"))
    assert.equal(requests.filter((c)=>c.url === "/messages/read-all").length,1)
    await act(async()=>{finish({updated:2});await wait()})
  })

  await test("消息已读失败保留红点并可重试，聚焦和点击外部可操作", async () => {
    let fail = true
    await mount(<AppLayout><p>测试首页</p></AppLayout>, {roleCode:"SYS_ADMIN",handler:(c) => {
      if(c.url === "/messages/unread-count") return {count:2}
      if(c.url === "/messages/read-all") {if(fail) throw new Error("标记暂时失败");return {updated:2}}
    }})
    await act(async()=>{document.querySelector('[aria-label="消息，2 条未读"]').focus();await wait()})
    await click(button("全部标为已读"))
    assert.match(text(),/标记暂时失败/)
    assert.ok(document.querySelector('[aria-label="消息，2 条未读"]'))
    fail=false
    await click(button("全部标为已读"))
    assert.equal(requests.filter((c)=>c.url === "/messages/read-all").length,2)
    await act(async()=>{document.body.dispatchEvent(new Event("pointerdown",{bubbles:true}));await wait()})
    assert.equal(button("全部标为已读"),undefined)
  })

  await test("历史报告预览旧版本并定位旧问题，时间轴不混入当前日期", async () => {
    const oldIssue = { id: 8001, title: "旧问题", category: "TIME", severity: "WARN", material_id: 12, material_version_id: 401, location: { page_no: 2, node_code: "T02" } }
    await mount(<ReviewWorkspacePage />, { path: "/review/submissions/101?report=111", pattern: "/review/submissions/:id", roleCode: "BRANCH_REVIEWER", handler: c => {
      if (c.url === "/submissions/101") return { ...baseSubmission, status: "BRANCH_REVIEW", materials: [{ id: 12, title: "材料", current_version_id: 402, version_no: 2 }], can: { add_issue: true, review: true } }
      if (c.url === "/reports/111") return { ...baseReport, id: 111, submission_id: 101, issues_by_category: { TIME: [oldIssue] }, material_versions: [{ material_id: 12, version_id: 401, version_no: 1 }], timeline_snapshot: { node_inputs: { T02: { date: "2020-01-02", value_kind: "DATE" } } } }
      if (c.url === "/archives/1/timeline") return { nodes: [{ code: "T02", effective: { date: "2026-10-29" } }] }
    } })
    assert.ok(requests.some(r => r.url === "/materials/12/pages/1" && r.params?.version_id === 401))
    assert.ok(!requests.some(r => /\/materials\/12\/pages\//.test(r.url) && r.params?.version_id === 402))
    await click([...document.querySelectorAll("button")].find(b => b.textContent.trim() === "旧问题"))
    assert.ok(requests.some(r => r.url === "/materials/12/pages/2" && r.params?.version_id === 401))
    assert.equal(button("确认问题"), undefined)
    await click(button("时间节点"))
    assert.ok(text().includes("2020-01-02"))
    assert.ok(!text().includes("2026-10-29"))
  })

  await test("历史报告加载失败不会回退为可编辑的当前审核", async () => {
    for (const student of [false, true]) {
      await mount(student ? <SelfCheckPage /> : <ReviewWorkspacePage />, { path: student ? "/my/self-check/101?report=111" : "/review/submissions/101?report=111", pattern: student ? "/my/self-check/:submissionId" : "/review/submissions/:id", roleCode: student ? "STUDENT" : "BRANCH_REVIEWER", handler: c => {
        if (c.url === "/reports/111") throw new Error("历史报告暂不可用")
        if (c.url === "/submissions/101") return { ...baseSubmission, can: { submit: true, add_issue: true, ai_check: true, review: true } }
      } })
      assert.ok(text().includes("历史报告暂不可用"))
      assert.equal(button("新增问题"), undefined)
      assert.equal(button("提交审核"), undefined)
      assert.ok(button("返回最新报告"))
    }
  })

  await test("可编辑材料可重新解析，接口失败保留页面供重试", async () => {
    await mount(<MaterialDetailPage />, { path: "/materials/12", pattern: "/materials/:id", roleCode: "BRANCH_REVIEWER", handler: c => {
      if (c.url === "/submissions/101") return { ...baseSubmission, can: { upload: true } }
      if (c.url === "/materials/12/retry-parse") throw new Error("解析服务暂不可用")
    } })
    await click(button("重新解析（使用当前模型配置）"))
    assert.match(text(), /解析服务暂不可用/)
    assert.equal(button("重新解析（使用当前模型配置）").disabled, false)
    assert.equal(requests.filter(c => c.url === "/materials/12/retry-parse").length, 1)
  })
  await test("投递检查只检查配置并明确不发送", async () => {
    await mount(<CompleteSettingsPage />, { roleCode: "SYS_ADMIN", handler: c => c.url === "/settings" ? { delivery: {} } : c.url === "/settings/delivery/test" ? { message: "未发送任何消息", email_ready: false, sms_ready: false, sent: false } : undefined })
    await click(button("消息与通知"))
    await click(button("检查投递配置（不发送）"))
    assert.match(text(), /未发送任何消息/)
    assert.equal(requests.filter(c => c.method === "post").length, 1)
    await mount(<CompleteSettingsPage />, { roleCode: "ORG_ADMIN", handler: c => c.url === "/settings" ? { delivery: {} } : undefined })
    assert.equal(button("检查投递配置（不发送）"), undefined)
  })
  await test("清空已保存的短信地址和密钥会发送明确清空值", async () => {
    await mount(<CompleteSettingsPage />, { roleCode: "SYS_ADMIN", handler: c => {
      if (c.url === "/settings" && c.method === "get") return { delivery: { sms_url: "https://sms.invalid/send", sms_api_key_set: true } }
      if (c.url === "/settings" && c.method === "put") return { delivery: { sms_url: "", sms_api_key_set: false } }
    } })
    await click(button("消息与通知"))
    await input(document.querySelector('[aria-label="短信服务 HTTPS 接口"]'), "")
    const clearKey = [...document.querySelectorAll('input[type="checkbox"]')].find(node => node.parentElement.textContent.includes("清除短信 API 密钥"))
    await click(clearKey)
    await click(button("保存邮件与短信服务配置"))
    const body = JSON.parse(requests.find(c => c.method === "put").data)
    assert.equal(body.delivery.sms_url, "")
    assert.equal(body.delivery.sms_api_key, "")
    assert.equal(document.querySelector('[aria-label="短信服务 HTTPS 接口"]').value, "")
  })
  await test("到期材料确认保留带原因并刷新待处理清单", async () => {
    let kept = false
    await mount(<CompleteSettingsPage />, { roleCode: "ORG_ADMIN", handler: c => {
      if (c.url === "/settings") return {}
      if (c.url === "/settings/retention/materials/402/keep") { kept = true; return { preserved: true } }
      if (c.url === "/settings/retention/materials") return { items: kept ? [] : [{ id: 402, title: "测试材料", filename: "原件.pdf", version_no: 2, due_at: "2026-01-01" }], total: kept ? 0 : 1, material_years: 10, page: 1, page_size: 20 }
    } })
    await click(button("查看到期待处理材料"))
    await input(document.querySelector('[aria-label="到期材料保留原因"]'), "仍需核查，保留原件")
    await click(button("确认保留原件"))
    assert.deepEqual(JSON.parse(requests.find(c => c.method === "post").data), { reason: "仍需核查，保留原件" })
    assert.match(text(), /暂无符合条件的材料/)
    assert.equal(requests.some(c => c.method === "delete"), false)
  })
  await test("已确认保留材料可查看确认人、时间和原因", async () => {
    await mount(<CompleteSettingsPage />, { roleCode: "ORG_ADMIN", handler: c => {
      if (c.url === "/settings") return {}
      if (c.url === "/settings/retention/materials") return { items: [{ id: 402, title: "测试材料", filename: "原件.pdf", version_no: 2, due_at: "2026-01-01", confirmation: { confirmed_by: "测试管理员", confirmed_at: "2026-10-26T10:00:00+08:00", reason: "仍需核查" } }], total: 1, material_years: 10, page: 1, page_size: 20 }
    } })
    await click(button("查看已确认保留"))
    assert.match(text(), /测试管理员.*2026-10-26.*仍需核查/)
    assert.equal(button("确认保留原件"), undefined)
    assert.equal(requests.find(c => c.url === "/settings/retention/materials").params.status, "confirmed")
  })
  await test("视觉 OCR 配置使用独立密钥且测试已保存配置", async () => {
    const settings = { ocr_vision: { enabled: false, allow_image_upload: false, model: "vision-test", base_url: "https://vision.invalid/v1", confidence_threshold: 0.9 } }
    await mount(<CompleteSettingsPage />, { roleCode: "SYS_ADMIN", handler: (c) => c.url === "/settings" ? settings : c.url === "/settings/ai/test" ? { ok: true, message: "图片识别通过", latency_ms: 1 } : undefined })
    await input(document.querySelector('[aria-label="视觉模型 API 密钥"]'), "synthetic-vision-key")
    await click(button("保存视觉 OCR 复核"))
    const body = JSON.parse(requests.find((c) => c.method === "put").data)
    assert.equal(body.ocr_vision.api_key, "synthetic-vision-key")
    assert.equal(body.ai, undefined)
    assert.equal(document.querySelector('[aria-label="视觉模型 API 密钥"]').value, "")
    await click(button("测试视觉 OCR 复核"))
    assert.deepEqual(JSON.parse(requests.find((c) => c.url === "/settings/ai/test").data), { target: "ocr_vision" })
    assert.match(text(), /图片识别通过/)
  })
  await test("视觉 OCR 建议先对照后保存，不自动覆盖原文", async () => {
    let saved
    const parsed = { material_id: 12, version_id: 401, full_text: "申请日期2026年10月2日", extracted_fields: {}, extractions: [], pages: [{ page_no: 1, text: "申请日期2026年10月2日", vision_reviews: [{ block_index: 0, bbox: [10, 20, 90, 50], status: "pending", original_text: "申请日期2026年10月2日", candidate_text: "申请日期2026年10月24日", confidence: 0.95, uncertain: false, model: "vision-test" }] }] }
    await mount(<ParsedTextPanel parsed={parsed} editable onSave={(body) => { saved = body }} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(document.querySelector("textarea").value, parsed.full_text)
    assert.equal(saved, undefined)
    assert.equal(button("核对后填入校正文本").disabled, true)
    await click([...document.querySelectorAll("label")].find((label) => label.textContent.includes("我已对照原图核对上述变化")).querySelector("input"))
    await click(button("核对后填入校正文本"))
    assert.equal(document.querySelector("textarea").value, "申请日期2026年10月24日")
    assert.equal(saved, undefined)
    await click(button("查看原图区域"))
    assert.ok(requests.some((r) => r.url === "/materials/12/pages/1" && r.params.version_id === 401))
    assert.equal(document.querySelector("textarea").value, "申请日期2026年10月24日")
    await click(button("收起复核原图"))
    await click(button("保存校正"))
    assert.equal(saved.corrected_text, "申请日期2026年10月24日")
    assert.equal(parsed.full_text, "申请日期2026年10月2日")
    await mount(<ParsedTextPanel parsed={parsed} editable={false} />)
    assert.equal(button("核对后填入校正文本"), undefined)
  })

  for (const retryFirst of [false, true]) {
    await test(retryFirst ? "密码文件下载失败保留口令并可重试" : "导入后下载加密密码文件并禁止再次领取", async () => {
      let downloads = 0
      await mount(<UsersPage />, { path: "/admin/users", roleCode: "ORG_ADMIN", handler: (config) => {
        if (config.url === "/users") return { items: [], total: 0, page: 1, page_size: 20 }
        if (config.url === "/users/import") return { total: 1, valid: 1, created_users: 1, created_archives: 0, errors: [],
          initial_passwords_file: { id: 9, password: "test-file-unlock", file_name: "passwords.xlsx" } }
        if (config.url === "/users/import-passwords/9/download") {
          downloads += 1
          if (retryFirst && downloads === 1) throw new Error("下载暂时失败")
          return new Blob(["synthetic-encrypted-file"])
        }
        return undefined
      } })
      await click(button("批量导入"))
      const picker = document.querySelectorAll('input[type="file"]')[1]
      Object.defineProperty(picker, "files", { value: [new File(["synthetic"], "users.xlsx")], configurable: true })
      await act(async () => picker.dispatchEvent(new Event("change", { bubbles: true })))
      await flush()
      await click(button("确认并导入"))
      assert.match(text(), /test-file-unlock/)
      await click(button("批量导入"))
      assert.equal(document.getElementById("user-import-panel").hidden, true)
      await click(button("查看导入结果"))
      assert.equal(document.getElementById("user-import-panel").hidden, false)
      assert.match(text(), /test-file-unlock/)
      assert.equal(document.body.textContent.includes("复制账号和密码"), false)
      await click(button("下载密码文件"))
      if (retryFirst) {
        assert.match(text(), /下载暂时失败/)
        assert.match(text(), /test-file-unlock/)
        assert.equal(button("下载密码文件").disabled, false)
        await click(button("下载密码文件"))
      }
      assert.equal(downloads, retryFirst ? 2 : 1)
      assert.equal(button("已下载").disabled, true)
    })
  }
  await test("完整档案编辑提交姓名生日扩展资料和所属批次", async () => {
    await mount(<ArchiveDetailPage />, { path:"/archives/1", pattern:"/archives/:id", roleCode:"ORG_ADMIN", handler:(c) => c.method === "put" ? {} : undefined })
    await click(button("编辑"))
    await input(document.querySelector('[aria-label="姓名"]'),"校正姓名")
    await input(document.querySelector('[aria-label="出生日期"]'),"2004-05-12")
    await input(document.querySelector('[aria-label="扩展资料"]'),'{"来源":"测试"}')
    await click(button("保存"))
    const body = JSON.parse(requests.find((c) => c.method === "put").data)
    assert.equal(body.real_name,"校正姓名"); assert.equal(body.birth_date,"2004-05-12"); assert.equal(body.branch_id,2); assert.deepEqual(body.profile_extra,{来源:"测试"})
  })
  await test("锁定时间节点只向显式授权的组织部入口开放", async () => {
    const timeline = {nodes:[{code:"T02",name:"申请日期",locked:true,effective:{date:"2026-01-01"},sources:[]}],derived:[]}
    await mount(<TimelineView timeline={timeline} onCorrect={() => {}} />)
    assert.equal(button("更正已锁定节点"),undefined)
    await mount(<TimelineView timeline={timeline} allowLockedCorrection onCorrect={() => {}} />,{roleCode:"ORG_ADMIN"})
    assert.ok(button("更正已锁定节点"))
  })
  await test("只修改用户姓名时不发送角色替换，原多身份保持不变", async () => {
    await mount(<UsersPage />, {roleCode:"SYS_ADMIN",handler:(c) => {
      if(c.url === "/users" && c.method === "get") return {items:[{id:7,username:"tester",real_name:"测试",org_id:2,is_active:true,roles:[{role:"STUDENT",org_id:2},{role:"BRANCH_REVIEWER",org_id:2}]}],total:1,page:1,page_size:20}
      if(c.url === "/users/7" && c.method === "put") return {}
    }})
    await click(button("编辑"))
    assert.equal(document.querySelectorAll('[aria-label$="角色"]').length,2)
    await click(button("保存"))
    const body = JSON.parse(requests.find((c) => c.method === "put").data)
    assert.equal("roles" in body,false)
  })
  await test("批次表单保存全部五级截止日且允许关闭已有档案批次", async () => {
    const row = {id:1,name:"测试批次",year:2026,term:"FULL_YEAR",stage_codes:[1],start_date:"2026-01-01",end_date:"2026-12-31",status:"ACTIVE",archive_count:2}
    await mount(<BatchesPage />, {roleCode:"ORG_ADMIN",handler:(c) => c.url === "/batches" ? {items:[row],total:1,page:1,page_size:20} : c.method === "put" ? {} : undefined})
    await click(button("编辑"))
    await input(document.querySelector('[aria-label="学生自查截止"]'),"2026-02-01")
    await input(document.querySelector('[aria-label="交叉互查截止"]'),"2026-04-01")
    await input(document.querySelector('[aria-label="组织部备案截止"]'),"2026-06-01")
    await click(button("保存"))
    const body = JSON.parse(requests.find((c) => c.method === "put").data)
    assert.equal(body.self_deadline,"2026-02-01"); assert.equal(body.cross_deadline,"2026-04-01"); assert.equal(body.org_deadline,"2026-06-01")
    await click(button("关闭批次"))
    assert.match(text(),/已有档案和审核记录保留/)
  })
  for (const action of ["关闭批次", "删除"]) {
    await test(`批次${action}失败保留确认框且允许重试`, async () => {
      let attempts = 0, exists = true
      const row = {id:4,name:"测试空批次",status:"ACTIVE",archive_count:0}
      await mount(<BatchesPage />, {roleCode:"ORG_ADMIN",handler:c=>{
        if(c.url === "/batches") return {items:exists ? [row] : [],total:exists ? 1 : 0,page:1,page_size:20}
        if(c.url === "/batches/4") { if(++attempts === 1) throw new Error("测试业务冲突"); exists=false; return {} }
      }})
      await click(button(action));await click(button("确认"))
      assert.match(document.querySelector("dialog").textContent,/测试业务冲突/)
      assert.equal(button("确认").disabled,false)
      await click(button("确认"))
      assert.equal(attempts,2);assert.equal(document.querySelector("dialog"),null)
    })
  }

  await test("系统设置按组保存，组织部不能修改安全和任务参数", async () => {
    const settings = {ai:{},ocr:{},worker:{concurrency:2},security:{max_failed_login:5},calendar:{holidays:[]},notification:{},retention:{},upload:{}}
    await mount(<CompleteSettingsPage />, {roleCode:"SYS_ADMIN",handler:(c) => c.url === "/settings" ? settings : undefined})
    await click(button("账号与运行"))
    await input(document.querySelector('[aria-label="任务并发数"]'),"3")
    await click(button("保存后台任务"))
    assert.deepEqual(JSON.parse(requests.find((c) => c.method === "put").data),{worker:{concurrency:3}})
    await mount(<CompleteSettingsPage />, {roleCode:"ORG_ADMIN",handler:(c) => c.url === "/settings" ? settings : undefined})
    assert.equal(button("保存后台任务"), undefined)
    assert.equal(button("保存日历").disabled,false)
  })
  await test("规则试运行传递临时覆盖并展示具体新增问题", async () => {
    await mount(<RuleVersionsPage />, {roleCode:"ORG_ADMIN",handler:(c) => {
      if(c.url === "/rules/versions") return {items:[]}
        if(c.url === "/rules/dry-run") return {results:[{submission_id:101,current:{summary:{total:2,by_severity:{BLOCK:1,WARN:1}}},trial:{summary:{total:3,by_severity:{BLOCK:1,WARN:2}}},added:["x"],removed:[],added_items:[{rule_code:"R-T01",title:"年龄测试问题",description:"测试详情"}]}]}
    }})
    await input(document.querySelector('input[placeholder*="提交包 ID"]'),"101")
    await input(document.querySelector('[aria-label="临时规则参数"]'),'{"time_rules":[{"code":"R-T01","is_active":false}]}')
    await click(button("试运行"))
    const body = JSON.parse(requests.find((c) => c.url === "/rules/dry-run").data)
    assert.equal(body.overrides.time_rules[0].is_active,false); assert.match(text(),/年龄测试问题/)
      assert.match(text(),/当前规则：2 个问题/); assert.match(text(),/临时规则：3 个问题/)
  })
  await test("导出页面实际提供阶段和批次控件并携带筛选", async () => {
    await mount(<ExportPage />, {roleCode:"ORG_ADMIN",handler:(c) => {
      if(c.url === "/stats/export") return {job_id:77}
      if(c.url === "/jobs/77") return {id:77,status:"FAILED",error:"测试终止"}
    }})
    const selects = [...document.querySelectorAll("label")]
    await input(selects.find((e) => e.textContent.startsWith("批次")).querySelector("select"),"1")
    await input(selects.find((e) => e.textContent.startsWith("阶段")).querySelector("select"),"3")
    await click(button("生成 Excel"))
    const body = JSON.parse(requests.find((c) => c.url === "/stats/export").data)
    assert.equal(body.filters.stage_code,"3"); assert.equal(body.filters.batch_id,"1")
  })

  await test("学生发展进度页正常加载时间节点与审核轨迹，且不重复展示", async () => {
    await mount(<MyProgressPage />, {
      path: "/my/progress",
      handler: (config) => {
        if (config.url === "/archives/1/history") return [
          { time: "2026-10-20T10:00:00", kind: "REVIEW", title: "PASS", detail: "审核通过", actor_name: "审核员", link_type: "submission", link_id: 101 },
          { time: "2026-10-21T10:00:00", kind: "FILED", title: "FILE", actor_name: "组织部", link_type: "submission", link_id: 101 },
          { time: "2026-10-19T10:00:00", kind: "UPLOAD", title: "上传材料（第 2 版）", link_type: "material", link_id: 12, version_id: 401 },
          { time: "2026-10-19T11:00:00", kind: "AI_REPORT", title: "AI 检查报告 #2 · 已完成", link_type: "submission", link_id: 101 },
          { time: "2026-10-19T12:00:00", kind: "ISSUE_RESPONSE", title: "提交整改回复", detail: "已补充说明", link_type: "submission", link_id: 101 },
          { time: "2026-10-19T13:00:00", kind: "NODE_CORRECTION", title: "校正申请日期", detail: "核对原件", link_type: "archive", link_id: 1 },
        ]
        if (config.url === "/archives/1/timeline") return { stages: [], nodes: [{ code: "N1", name: "递交入党申请", effective: { date: "2025-10-10" }, sources: [] }], derived: [] }
        return undefined
      },
    })
    assert.match(text(), /发展历史/)
    assert.match(text(), /审核通过/)
    for (const event of ["备案归档", "第 2 版", "AI 检查报告", "已补充说明", "校正申请日期"]) assert.ok(text().includes(event))
    assert.ok(document.querySelector('a[href="/materials/12?version_id=401"]'))
    assert.match(text(), /递交入党申请/)
    assert.equal([...document.querySelectorAll("h2")].filter((node) => node.textContent === "时间节点").length, 1)
    assert.equal(document.querySelectorAll('[aria-label="阶段进度说明"]').length, 1)
  })

  await test("互查审核人按角色授权组织显示，且不能重复分配", async () => {
    await mount(<CrossReviewConfigPage />, {
      path: "/review/cross-config",
      roleCode: "ORG_ADMIN",
      handler: (config) => {
        if (config.url === "/batches") return { items: [{ id: 1, name: "测试批次" }] }
        if (config.url === "/orgs") return [
          { id: 1, name: "学校", org_type: "SCHOOL", parent_id: null },
          { id: 2, name: "学院", org_type: "COLLEGE", parent_id: 1 },
          { id: 3, name: "支部甲", org_type: "BRANCH", parent_id: 2 },
          { id: 4, name: "支部乙", org_type: "BRANCH", parent_id: 2 },
          { id: 5, name: "支部丙", org_type: "BRANCH", parent_id: 2 },
        ]
        if (config.url === "/batches/1/cross-review-pairs") return []
        if (config.url === "/users") return { items: [{ id: 11, real_name: "互查员甲", org_id: 1, roles: [{ role: "CROSS_REVIEWER", org_id: 5 }] }] }
        return undefined
      },
    })
    const branchA = document.querySelector('[aria-label="支部甲的互查支部"]')
    const branchB = document.querySelector('[aria-label="支部乙的互查支部"]')
    await input(branchA, "5")
    const reviewerA = document.querySelector('[aria-label="支部甲的指定审核人"]')
    assert.ok([...reviewerA.options].some((option) => option.value === "11" && option.text.includes("互查员甲")))
    await input(reviewerA, "11")
    await input(branchB, "5")
    const reviewerB = document.querySelector('[aria-label="支部乙的指定审核人"]')
    assert.equal([...reviewerB.options].some((option) => option.value === "11" && option.disabled), true)
  })

  await test("交叉互查配对加载失败时阻止保存，避免空配置覆盖原安排", async () => {
    await mount(<CrossReviewConfigPage />, {
      path: "/cross-review",
      roleCode: "ORG_ADMIN",
      handler: (config) => {
        if (config.url === "/batches") return { items: [{ id: 1, name: "测试批次" }] }
        if (config.url === "/orgs") return [
          { id: 2, name: "测试学院", org_type: "COLLEGE", parent_id: 1 },
          { id: 3, name: "测试支部甲", org_type: "BRANCH", parent_id: 2 },
          { id: 4, name: "测试支部乙", org_type: "BRANCH", parent_id: 2 },
        ]
        if (config.url === "/batches/1/cross-review-pairs") throw new Error("当前配对读取失败")
        if (config.url === "/users") return { items: [] }
        return undefined
      },
    })
    assert.match(text(), /当前不会保存空配置/)
    assert.equal(button("保存配对").disabled, true)
    assert.equal(requests.some((request) => request.url === "/batches/1/cross-review-pairs" && request.method === "put"), false)
  })

  await test("系统配置保存真实上传限制字段并要求确认重建演示数据", async () => {
    await mount(<SettingsPage />, {
      path: "/admin/settings",
      roleCode: "ORG_ADMIN",
      handler: (config) => {
        if (config.url === "/settings" && config.method === "get") return {
          ai: { base_url: "", model: "", timeout_s: 30, max_concurrency: 1, llm_enabled: false, desensitize: true },
          ocr: { engine: "", available_engines: [] },
          upload: { max_file_mb: 20, max_zip_mb: 500, allowed_ext: ["pdf"] },
          retention: { material_years: 10, export_days: 7 },
          calendar: { period_min_tail_days: 30, holidays: ["2026-10-01"], extra_workdays: ["2026-10-10"] },
        }
        if (config.url === "/settings" && config.method === "put") return {}
        if (config.url === "/admin/seed-demo") return { orgs: 9, users: 20, archives: 24, materials: 48 }
        return undefined
      },
    })
    await click(button("保存上传限制"))
    const saved = JSON.parse(requests.find((request) => request.url === "/settings" && request.method === "put").data)
    assert.equal(saved.upload.max_file_mb, 20)
    assert.equal(saved.upload.max_zip_mb, 500)
    assert.equal("max_mb" in saved.upload, false)
    await click(button("保存保留期限"))
    const retentionSave = JSON.parse(requests.filter((request) => request.url === "/settings" && request.method === "put").at(-1).data)
    assert.equal(retentionSave.retention.export_days, 7)
    await click(button("保存日历"))
    const calendarSave = JSON.parse(requests.filter((request) => request.url === "/settings" && request.method === "put").at(-1).data)
    assert.deepEqual(calendarSave.calendar.holidays, ["2026-10-01"])
    assert.deepEqual(calendarSave.calendar.extra_workdays, ["2026-10-10"])
    assert.equal("holidays_text" in calendarSave.calendar, false)
    await click(button("维护工具"))
    await click(button("清理并重建"))
    assert.match(text(), /真实账号和真实材料不会被清理/)
    assert.equal(requests.some((request) => request.url === "/admin/seed-demo"), false)
    await click(button("确认重建"))
    const seedBody = JSON.parse(requests.find((request) => request.url === "/admin/seed-demo").data)
    assert.equal(seedBody.reset, true)
  })

  await test("批次管理可见全部五级截止时间与状态，空名称不能提交", async () => {
    await mount(<BatchesPage />, {
      path: "/admin/batches",
      roleCode: "ORG_ADMIN",
      handler: (config) => config.url === "/batches" ? { items: [], total: 0, page: 1, page_size: 20 } : undefined,
    })
    await click(button("新建批次"))
    for (const label of ["学生自查截止", "支部初审截止", "交叉互查截止", "学院复审截止", "组织部备案截止"]) assert.match(text(), new RegExp(label))
    assert.match(text(), /新建批次默认状态为“进行中”/)
    await click(button("保存"))
    assert.match(text(), /请填写批次名称/)
    assert.equal(requests.some((request) => request.url === "/batches" && request.method === "post"), false)
  })

  await test("报表导出使用批次和阶段选项，倒置日期不发起任务", async () => {
    await mount(<ExportPage />, {
      path: "/stats/export",
      roleCode: "ORG_ADMIN",
      handler: (config) => config.url === "/batches" ? { items: [{ id: 7, name: "2026 春季批次", year: 2026 }] } : undefined,
    })
    assert.match(text(), /2026 春季批次/)
    assert.match(text(), /确定入党积极分子/)
    const dates = ["开始日期", "结束日期"].map(name => [...document.querySelectorAll("label")].find(label => label.textContent.startsWith(name)).querySelector("input"))
    await input(dates[0], "2026-10-20")
    await input(dates[1], "2026-10-01")
    await click(button("生成 Excel"))
    assert.match(text(), /结束日期不能早于开始日期/)
    assert.equal(requests.some((request) => request.url === "/stats/export"), false)
  })

  await test("报表导出任务失败重试后重新轮询状态", async () => {
    let jobReads = 0
    await mount(<ExportPage />, {
      path: "/stats/export",
      roleCode: "ORG_ADMIN",
      handler: (config) => {
        if (config.url === "/batches") return { items: [] }
        if (config.url === "/stats/export") return { job_id: 88 }
        if (config.url === "/jobs/88") {
          jobReads += 1
          return jobReads === 1
            ? { id: 88, job_type: "EXPORT", status: "FAILED", error: "导出失败" }
            : { id: 88, job_type: "EXPORT", status: "RUNNING", total: 1, done_count: 0 }
        }
        if (config.url === "/jobs/88/retry") return {}
        return undefined
      },
    })
    await click(button("生成 Excel"))
    assert.match(text(), /导出失败/)
    await click(button("重试"))
    assert.ok(requests.some((request) => request.url === "/jobs/88/retry"))
    assert.ok(jobReads >= 2)
    assert.match(text(), /数据导出 · 运行中/)
  })

  await test("通知补全去重提交包编号并在成功后清空旧表单", async () => {
    await mount(<NoticesPage />, {
      path: "/notices",
      roleCode: "ORG_ADMIN",
      handler: (config) => {
        if (config.url === "/notices") return { items: [], total: 0, page: 1, page_size: 20 }
        if (config.url === "/submissions/completion-notices") return { created: [{ id: 1 }, { id: 2 }], skipped: [] }
        return undefined
      },
    })
    await click(button("批量补全提示"))
    await input(document.querySelector(".modal input"), "10, 10, 11")
    await click(button("生成并推送"))
    const body = JSON.parse(requests.find((request) => request.url === "/submissions/completion-notices").data)
    assert.deepEqual(body.submission_ids, [10, 11])
    await click(button("批量补全提示"))
    assert.equal(document.querySelector(".modal input").value, "")
  })

  await test("通知列表校验提交包 ID，非法输入不发送查询", async () => {
    await mount(<NoticesPage />, {
      path: "/notices",
      roleCode: "ORG_ADMIN",
      handler: (config) => config.url === "/notices" ? { items: [], total: 0, page: 1, page_size: 20 } : undefined,
    })
    const submissionIdInput = [...document.querySelectorAll("label")]
      .find((node) => node.textContent.includes("提交包 ID"))?.querySelector("input")
    await input(submissionIdInput, "abc")
    assert.match(text(), /提交包 ID 只能填写正整数/)
    assert.equal(requests.filter((request) => request.url === "/notices").length, 1)

    await input(submissionIdInput, "123")
    const noticeRequests = requests.filter((request) => request.url === "/notices")
    assert.equal(noticeRequests.length, 2)
    assert.equal(noticeRequests[1].params.submission_id, "123")
    assert.doesNotMatch(text(), /提交包 ID 只能填写正整数/)

    await mount(<NoticesPage />, {
      path: "/notices?submission_id=abc",
      roleCode: "ORG_ADMIN",
      handler: (config) => config.url === "/notices" ? { items: [], total: 0, page: 1, page_size: 20 } : undefined,
    })
    assert.match(text(), /提交包 ID 只能填写正整数/)
    assert.equal(requests.filter((request) => request.url === "/notices").length, 1)
    assert.equal(requests.find((request) => request.url === "/notices").params.submission_id, undefined)
  })

  await test("档案列表缺少阶段名时正常显示，互查角色无新建按钮", async () => {
    await mount(<ArchiveListPage />, { path: "/archives", roleCode: "CROSS_REVIEWER" })
    assert.match(text(), /测试学生/)
    assert.match(text(), /申请入党/)
    assert.equal(button("新建档案"), undefined)
  })

  await test("档案查询失败显示错误与重试，不显示空列表", async () => {
    await mount(<ArchiveListPage />, { path: "/archives", roleCode: "BRANCH_REVIEWER", handler: (config) => { if (config.url === "/archives") throw new Error("档案服务连接失败") } })
    assert.match(text(), /档案服务连接失败/)
    assert.ok(button("重试"))
    assert.doesNotMatch(text(), /暂无数据/)
  })

  await test("档案保存失败后保留输入并显示原因", async () => {
    await mount(<ArchiveDetailPage />, { path: "/archives/1", pattern: "/archives/:id", roleCode: "BRANCH_REVIEWER", handler: (config) => { if (config.method === "put") throw new Error("当前无权修改档案") } })
    await click(button("编辑"))
    await input(document.querySelector('[aria-label="专业"]'), "计算机")
    await click(button("保存"))
    assert.match(text(), /当前无权修改档案/)
    assert.equal(document.querySelector('[aria-label="专业"]').value, "计算机")
  })

  await test("仪表盘显示实时必需清单，超额材料不掩盖缺项", async () => {
    await mount(<StudentDashboard data={{ archive_id: 1, submission: { id: 101 }, current_stage: 1 }} />, { handler: (config) => config.url.endsWith("/completeness") ? { items: [{ required: true, expected: 1, actual: 4 }, { required: true, expected: 1, actual: 0 }] } : undefined })
    assert.match(text(), /必需材料 1\/2/)
  })

  await test("自查报告直接展示，提交后明确等待审核", async () => {
    await mount(<SelfCheckPage />, { path: "/my/self-check/101", pattern: "/my/self-check/:submissionId", handler: (c) => c.url === "/submissions/101" ? { ...baseSubmission, status: "BRANCH_REVIEW", can: { submit: false } } : undefined })
    const report = document.querySelector('[aria-label="自查报告与材料清单"]')
    assert.ok(report)
    assert.equal(report.closest("details"), null)
    assert.match(document.querySelector('[aria-label="当前办理指引"]').textContent, /等待审核/)
    assert.doesNotMatch(text(), /当前状态或角色不可提交/)
    assert.equal(button("发起自查"), undefined)
    assert.equal(button("提交审核"), undefined)
  })

  await test("整改默认只展示未回复问题，全部问题可切换并保留材料返回来源", async () => {
    await mount(<RectificationPage />, { path: "/my/rectification", handler: (c) => {
      if (c.url === "/submissions/101") return { ...baseSubmission, status: "RETURNED" }
      if (c.url === "/submissions/101/issues") return { items: [
        { id: 7, material_id: 12, category: "OTHER", message: "待修改测试内容", severity: "WARN", review_status: "CONFIRMED" },
        { id: 8, category: "OTHER", message: "已回复测试内容", severity: "WARN", review_status: "CONFIRMED", response_type: "EXPLAINED", response_text: "这是已经保存的回复说明" },
      ] }
    } })
    assert.ok(button("待我回复（1）"))
    assert.doesNotMatch(text(), /这是已经保存的回复说明/)
    assert.equal(button("重新提交").disabled, true)
    assert.ok([...document.querySelectorAll("a")].some(a => a.getAttribute("href") === "/materials/12?issue_id=7&from=rectification"))
    await click(button("全部问题（2）"))
    assert.match(text(), /这是已经保存的回复说明/)
    await click(button("待我回复（1）"))
    assert.doesNotMatch(text(), /这是已经保存的回复说明/)
  })

  for (const page of ["rectification", "self-check"]) {
    await test(`${page}问题筛选及范围切换保留整改草稿，失败可重试`, async () => {
      let saved = false, attempts = 0
      const issue = { id: 7, material_id: 12, category: "CONTENT", title: "测试问题", severity: "WARN", review_status: "CONFIRMED" }
      await mount(page === "rectification" ? <RectificationPage /> : <SelfCheckPage />, { path: page === "rectification" ? "/my/rectification" : "/my/self-check/101", pattern: page === "rectification" ? "/my/rectification" : "/my/self-check/:submissionId", handler: c => {
        if (c.url === "/submissions/101") return { ...baseSubmission, status: "RETURNED" }
        if (c.url === "/submissions/101/issues") return { items: [{ ...issue, ...(saved ? {response_type:"EXPLAINED",response_text:"这是一份尚未保存的整改草稿"} : {}) }] }
        if (c.url === "/issues/7/response") { if (++attempts === 1) throw new Error("测试保存失败"); saved = true; return {} }
      } })
      const draft = "这是一份尚未保存的整改草稿"
      await input(document.querySelector('[aria-label="整改说明"]'), draft)
      if (page === "rectification") { await click(button("全部问题（1）")); await click(button("待我回复（1）")) }
      await input(document.querySelector('[aria-label="问题级别"]'), "BLOCK")
      assert.equal(document.querySelector('[aria-label="整改说明"]'), null)
      await input(document.querySelector('[aria-label="问题级别"]'), "")
      assert.equal(document.querySelector('[aria-label="整改说明"]').value, draft)
      await click(button("保存情况说明"))
      assert.match(text(), /测试保存失败/)
      assert.equal(document.querySelector('[aria-label="整改说明"]').value, draft)
      await click(button("保存情况说明"))
      assert.equal(attempts, 2)
      assert.equal(JSON.parse(requests.filter(r => r.url === "/issues/7/response").at(-1).data).response_text, draft)
    })
  }

  await test("组织管理包含停用组织，管理按钮遵守实际角色权限", async () => {
    const tree = [{ id: 1, name: "学校", org_type: "SCHOOL", is_active: true, children: [{ id: 2, name: "停用学院", org_type: "COLLEGE", is_active: false, children: [] }] }]
    for (const roleCode of ["SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"]) {
      await mount(<OrgsPage />, { roleCode, handler: c => c.url === "/orgs" ? tree : undefined })
      assert.equal(requests.find(r => r.url === "/orgs").params.include_inactive, true)
      assert.match(text(), /停用学院/)
      assert.equal(!!button("删除"), roleCode === "SYS_ADMIN")
      assert.equal(!!button("编辑"), roleCode !== "COLLEGE_REVIEWER")
      assert.equal(!!button("新增学校"), roleCode !== "COLLEGE_REVIEWER")
    }
  })

  await test("刷新任务同时更新已打开的任务明细，失败可在明细重试", async () => {
    let reads = 0
    await mount(<JobsPage />, { path: "/tasks/jobs?view=all", roleCode: "SYS_ADMIN", handler: c => {
      if (c.url === "/jobs") return { items: [{id:77,job_type:"PARSE",status:"RUNNING"}],total:1,page:1,page_size:20 }
      if (c.url === "/jobs/77") { reads++; if (reads === 2) throw new Error("测试详情刷新失败"); return {id:77,job_type:"PARSE",status:reads > 2 ? "SUCCEEDED" : "RUNNING",progress:reads > 2 ? 100 : 15} }
    } })
    await click(button("材料解析"))
    assert.match(document.querySelector('[aria-label="任务明细"]').textContent, /运行中/)
    await click(button("刷新任务"))
    assert.equal(reads, 2)
    assert.match(document.querySelector('[aria-label="任务明细"]').textContent, /测试详情刷新失败/)
    await click([...document.querySelector('[aria-label="任务明细"]').querySelectorAll("button")].find(b => b.textContent === "重试"))
    assert.match(document.querySelector('[aria-label="任务明细"]').textContent, /已完成/)
  })

  await test("草稿报告过期时禁止提交", async () => {
    await mount(<SelfCheckPage />, { path: "/my/self-check/101", pattern: "/my/self-check/:submissionId", handler: (config) => config.url === "/submissions/101" ? { ...baseSubmission, latest_report: { ...baseReport, is_stale: true } } : undefined })
    assert.equal(button("提交审核")?.disabled, true)
    assert.match(text(), /重新自查/)
  })

  await test("运行中的自查恢复任务显示并禁止重复发起", async () => {
    await mount(<SelfCheckPage />, { path: "/my/self-check/101", pattern: "/my/self-check/:submissionId", handler: (config) => {
      if (config.url === "/submissions/101") return { ...baseSubmission, ai_status: "RUNNING", ai_job_id: 301 }
      if (config.url === "/jobs/301") return { id: 301, status: "RUNNING", progress: 50, stage_text: "正在检查材料" }
    } })
    assert.equal(button("自查进行中…")?.disabled, true)
    assert.match(text(), /正在检查材料/)
    assert.equal(requests.filter((request) => request.url.endsWith("/ai-check")).length, 0)
  })

  await test("退回整改允许旧报告重提，并追踪复核任务", async () => {
    let submitted = false
    await mount(<RectificationPage />, { path: "/my/rectification", handler: (config) => {
      const returned = { ...baseSubmission, status: "RETURNED", latest_report: { ...baseReport, is_stale: true } }
      if (config.url === "/submissions/101") return submitted ? { ...returned, status: "BRANCH_REVIEW", ai_status: "QUEUED", ai_job_id: 301, can: { submit: false } } : returned
      if (config.url === "/submissions/101/submit") { submitted = true; return { submission: { ...returned, status: "BRANCH_REVIEW", ai_status: "QUEUED", ai_job_id: 301, can: { submit: false } }, recheck_job_id: 301 } }
      if (config.url === "/jobs/301") return { id: 301, status: "RUNNING", progress: 20, stage_text: "正在复核整改" }
    } })
    assert.equal(button("重新提交")?.disabled, false)
    await click(button("重新提交"))
    assert.equal(requests.filter((request) => request.url === "/submissions/101/submit").length, 1)
    assert.match(text(), /正在复核整改/)
    assert.equal(button("重新提交"), undefined)
    assert.equal(document.querySelector('[aria-label="整改问题范围"]'), null)
  })

  await test("材料列表直接删除有确认，取消不请求，审核中隐藏删除", async () => {
    let removed = false
    const handler = (config) => {
      if (config.url === "/archives/1/materials") return [{ stage_code: 1, checklist: [{ checklist_item_id: 1, material_type: { id: 1, name: "测试材料" }, materials: removed ? [] : [{ id: 12, title: "虚构材料.pdf", current_version: { parse_status: "DONE" } }] }] }]
      if (config.url === "/materials/12" && config.method === "delete") { removed = true; return {} }
    }
    await mount(<MyMaterialsPage />, { path: "/my/materials", roleCode: "STUDENT", handler })
    assert.ok(document.querySelector('a[href="/materials/12"]'))
    await click(button("删除"))
    assert.match(text(), /删除这份材料/)
    await click(button("取消"))
    assert.equal(removed, false)
    await click(button("删除"))
    await click(button("确认删除"))
    assert.equal(removed, true)
    assert.equal(button("删除"), undefined)
    removed = false
    await mount(<MyMaterialsPage />, { path: "/my/materials", roleCode: "STUDENT", handler: (config) => {
      if (config.url === "/my/archive") return { ...baseArchive, current_submission: { id: 101, status: "BRANCH_REVIEW" } }
      return handler(config)
    } })
    assert.equal(button("删除"), undefined)
    assert.equal(button("上传该项"), undefined)
    assert.match(text(), /自查报告/)
    assert.doesNotMatch(text(), /按清单逐项上传|AI 自查与提交/)
  })

  await test("材料接口失败显示错误而非空清单", async () => {
    await mount(<MyMaterialsPage />, { path: "/my/materials", handler: (config) => { if (config.url === "/archives/1/materials") throw new Error("材料查询失败") } })
    assert.match(text(), /材料查询失败/)
  })

  await test("问题深链接定位历史版本与页码，历史解析不可编辑", async () => {
    const issue = { id: 51, material_id: 12, material_version_id: 401, title: "日期错误", category: "TIME", severity: "BLOCK", location: { page_no: 2, bbox: [10, 20, 90, 50] } }
    await mount(<MaterialDetailPage />, { path: "/materials/12?issue_id=51", pattern: "/materials/:id", roleCode: "BRANCH_REVIEWER", handler: (config) => config.url.endsWith("/issues") ? { items: [issue] } : undefined })
    assert.match(text(), /历史版本/)
    assert.match(text(), /问题定位：日期错误/)
    assert.ok(requests.some((request) => request.url === "/materials/12/pages/2" && Number(request.params.version_id) === 401))
    await click(button("解析文本"))
    assert.equal(document.querySelector("textarea")?.readOnly, true)
    assert.equal(button("保存校正"), undefined)
  })

  await test("所选版本对比使用明确的两个版本编号", async () => {
    await mount(<MaterialDetailPage />, { path: "/materials/12", pattern: "/materials/:id", roleCode: "BRANCH_REVIEWER" })
    await click(button("版本"))
    await click(button("对比所选版本"))
    const request = requests.find((item) => item.url === "/materials/12/diff")
    assert.deepEqual(request?.params, { from_version: 401, to_version: 402 })
    assert.match(text(), /测试新增文字/)
  })

  await test("切换材料时预览页码重置，避免向新材料请求旧页", async () => {
    await mount(<MaterialViewer materialId={12} versionId={402} page={3} />, {})
    await act(async () => root.render(<MaterialViewer materialId={13} versionId={403} />))
    await flush()
    assert.ok(requests.some((request) => request.url === "/materials/13/pages/1"))
  })

  await test("上传期间重复拖放只调用一次上传接口，同步异常显示错误", async () => {
    let calls = 0, finish
    await mount(<FileUploader onFile={() => { calls += 1; return new Promise((resolve) => { finish = resolve }) }} />, {})
    const target = document.querySelector('[class*="border-dashed"]')
    await act(async () => {
      for (let count = 0; count < 2; count += 1) {
        const event = new Event("drop", { bubbles: true, cancelable: true })
        Object.defineProperty(event, "dataTransfer", { value: { files: [new File(["PDF"], "sample.pdf")] } })
        target.dispatchEvent(event)
      }
      await wait()
    })
    assert.equal(calls, 1)
    await act(async () => { finish(); await wait() })
    await mount(<FileUploader onFile={() => { throw new Error("上传回调失败") }} />, {})
    const inputNode = document.querySelector('input[type="file"]')
    await act(async () => { Object.defineProperty(inputNode, "files", { value: [new File(["PDF"], "sample.pdf")] }); inputNode.dispatchEvent(new Event("change", { bubbles: true })); await wait() })
    assert.match(text(), /上传回调失败/)
  })

  await test("待确认关键问题禁止通过，驳回后可通过", async () => {
    const submission = { ...baseSubmission, status: "BRANCH_REVIEW", level: "BRANCH", can: { review: true } }
    const issue = { id: 51, severity: "BLOCK", is_active: true, review_status: "PENDING", report_id: 201 }
    await mount(<ReviewDecisionPanel submission={submission} issues={[issue]} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("通过")?.disabled, true)
    await mount(<ReviewDecisionPanel submission={submission} issues={[{ ...issue, review_status: "REJECTED" }]} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("通过")?.disabled, false)
  })

  await test("驳回误报必须写理由，提交携带真实问题编号", async () => {
    await mount(<IssueActions issue={{ id: 51, review_status: "PENDING" }} />, { roleCode: "BRANCH_REVIEWER", handler: (config) => config.url === "/issues/51" ? {} : undefined })
    await click(button("驳回误报"))
    assert.equal(button("确认驳回（误报）")?.disabled, true)
    await input(document.querySelector('[aria-label="驳回理由"]'), "已核查原件，属于误报")
    await click(button("确认驳回（误报）"))
    const request = requests.find((item) => item.url === "/issues/51")
    assert.equal(JSON.parse(request?.data).note, "已核查原件，属于误报")
  })

  await test("ZIP 识别后必须确认入库，部分失败重试不再提交已入库项", async () => {
    const items = [
      { item_id: "zip-1", entry_path: "20260001_申请书.pdf", status: "MATCHED", matched_archive: { id: 1, real_name: "测试学生" } },
      { item_id: "zip-2", entry_path: "20260002_申请书.pdf", status: "MATCHED", matched_archive: { id: 2, real_name: "测试学生二" } },
    ]
    let assigns = 0
    await mount(<BatchUploadPage />, { path: "/materials/batch-upload", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/materials/batch-upload") return { job_id: 501 }
      if (config.url === "/jobs/501") return { id: 501, status: "SUCCEEDED", result: { items } }
      if (config.url === "/materials/batch-upload/501/assign") {
        assigns += 1
        return assigns === 1 ? { imported: 1, failed: 1, skipped: 0, items: [{ ...items[0], status: "IMPORTED", material_id: 12 }, { ...items[1], status: "FAILED", error: "文件处理失败" }] } : { imported: 1, failed: 0, skipped: 0, items: [{ ...items[1], status: "IMPORTED", material_id: 13 }] }
      }
    } })
    const fileInput = document.querySelector('input[type="file"]')
    await act(async () => { Object.defineProperty(fileInput, "files", { value: [new File(["ZIP"], "samples.zip")] }); fileInput.dispatchEvent(new Event("change", { bubbles: true })); await wait() })
    await flush()
    assert.ok(button("确认导入 2 个文件"))
    assert.equal(requests.filter((request) => request.url.endsWith("/assign")).length, 0)
    await click(button("确认导入 2 个文件"))
    assert.match(text(), /文件处理失败/)
    await click(button("确认导入 1 个文件"))
    const bodies = requests.filter((request) => request.url.endsWith("/assign")).map((request) => JSON.parse(request.data))
    assert.equal(bodies[0].assignments.length, 2)
    assert.deepEqual(bodies[1].assignments.map((item) => item.item_id), ["zip-2"])
  })

  await test("整改上传把真实新版本和说明保存到同一个问题", async () => {
    await mount(<IssueResponseForm issue={{ id: 51, material_id: 12 }} />, { handler: (config) => {
      if (config.url === "/materials/12/versions" && config.method === "post") return { version: { id: 403, version_no: 3 }, parse_job_id: 502, responded_issue_ids: [51] }
      if (config.url === "/issues/51/response") return {}
      if (config.url === "/jobs/502") return { id: 502, status: "SUCCEEDED", progress: 100 }
    } })
    await input(document.querySelector('[aria-label="整改说明"]'), "已经核对并修正了材料的日期")
    const fileInput = document.querySelector('input[type="file"]')
    await act(async () => { Object.defineProperty(fileInput, "files", { value: [new File(["PDF"], "fixed.pdf")] }); fileInput.dispatchEvent(new Event("change", { bubbles: true })); await wait() })
    await flush()
    const request = requests.find((item) => item.url === "/issues/51/response")
    assert.deepEqual(JSON.parse(request?.data), { response_type: "MODIFIED", response_text: "已经核对并修正了材料的日期", version_id: 403 })
    assert.match(text(), /已保存整改回复/)
  })

  await test("AI 失败任务点击重试后重新获取同一任务的完成状态", async () => {
    let retried = false
    await mount(<ReviewJobStatus jobId={503} />, { roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/jobs/503") return { id: 503, status: retried ? "SUCCEEDED" : "FAILED", error: retried ? null : "模型超时", progress: retried ? 100 : 20 }
      if (config.url === "/jobs/503/retry") { retried = true; return { id: 503 } }
    } })
    assert.match(text(), /模型超时/)
    await click(button("重试失败任务"))
    assert.match(text(), /已完成/)
    assert.equal(requests.filter((request) => request.url === "/jobs/503").length, 2)
  })

  await test("预览失败可原位重试并恢复图片", async () => {
    let attempt = 0
    await mount(<MaterialViewer materialId={12} versionId={402} />, { handler: (config) => {
      if (config.url === "/materials/12/pages/1" && ++attempt === 1) throw new Error("预览文件暂不可用")
    } })
    assert.match(text(), /预览文件暂不可用/)
    await click(button("重新加载预览"))
    assert.ok(document.querySelector('img[alt="第 1 页"]'))
  })

  await test("非当前审核层级的审核员不能修改材料类型与解析文本", async () => {
    await mount(<MaterialDetailPage />, { path: "/materials/12", pattern: "/materials/:id", roleCode: "BRANCH_REVIEWER", handler: (config) => config.url === "/submissions/101" ? { ...baseSubmission, status: "COLLEGE_REVIEW", can: { upload: false, review: false } } : undefined })
    assert.equal(button("确认类型")?.disabled, true)
    await click(button("解析文本"))
    assert.equal(document.querySelector("textarea")?.readOnly, true)
    assert.equal(button("保存校正"), undefined)
  })

  await test("审核员常用导航仅四项，规则分组可展开访问", async () => {
    await mount(<AppLayout><ReviewerDashboard data={{ todo: { to_review: 1 } }} /></AppLayout>, { roleCode: "BRANCH_REVIEWER" })
    const visibleLinks = () => [...document.querySelectorAll('nav[aria-label="主要导航"] a')].filter((link) => !link.closest("ul[hidden]"))
    assert.equal(visibleLinks().length, 4)
    await click(button("材料与审核标准"))
    assert.equal(visibleLinks().length, 7)
    assert.equal(button("材料与审核标准").getAttribute("aria-expanded"), "true")
  })

  await test("访问低频功能时对应菜单自动展开", async () => {
    await mount(<AppLayout><p>材料类型内容</p></AppLayout>, { path: "/rules/material-types", roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("材料与审核标准").getAttribute("aria-expanded"), "true")
    assert.equal(document.querySelector('a[href="/rules/checklists"]').closest("ul").hidden, false)
    assert.equal(document.querySelector('a[href="/rules/checklists"]').getAttribute("aria-current"), "page")
  })

  await test("相近规则页面通过同一栏目内的标签快速切换", async () => {
    const routes = [{ element: <RuleSectionLayout />, children: [
      { path: "/rules/checklists", element: <p>阶段清单内容</p> },
      { path: "/rules/material-types", element: <p>材料类型内容</p> },
    ] }]
    await mount(null, { path: "/rules/checklists", routes })
    assert.match(text(), /材料标准材料清单材料类型与模板阶段清单内容/)
    await click(document.querySelector('a[href="/rules/material-types"]'))
    assert.equal(router.state.location.pathname, "/rules/material-types")
    assert.match(text(), /材料类型内容/)
    assert.equal(document.querySelector('a[aria-current="page"]').getAttribute("href"), "/rules/material-types")
  })

  await test("学生首页主入口会随退回状态指向整改", async () => {
    await mount(<StudentDashboard data={{ archive_id: 1, submission: { id: 101, status: "RETURNED" } }} />)
    const primary = document.querySelector(".next-action .btn-primary")
    assert.equal(primary.getAttribute("href"), "/my/rectification")
    assert.equal(primary.querySelector("svg"), null)
    assert.equal(document.querySelector(".home-support-links"), null)
    assert.doesNotMatch(text(), /查看全部进度|查看全部事项/)
    assert.equal(document.querySelectorAll(".next-action .btn-primary").length, 1)
    assert.match(document.querySelector(".process-list .is-current").textContent, /整改与重新提交/)
    assert.equal(document.querySelector(".process-list .is-current a").getAttribute("href"), "/my/rectification")
    assert.ok(document.querySelector(".next-action .badge-soft"))
  })

  await test("高级筛选默认收起，但启用的筛选条件会显示数量并展开", async () => {
    const props = { fields: [{ key: "q", label: "姓名" }], advancedFields: [{ key: "has_block", label: "有无关键问题" }], onChange: () => {} }
    await mount(<FilterBar {...props} values={{}} />)
    assert.equal(document.querySelector("details").open, false)
    await mount(<FilterBar {...props} values={{ has_block: "false" }} />)
    assert.equal(document.querySelector("details").open, true)
    assert.match(text(), /已启用 1 项/)
  })

  await test("待办默认不显示勾选与批量按钮，启用批量模式后恢复操作", async () => {
    await mount(<ReviewTasksPage />, { path: "/review/tasks", roleCode: "BRANCH_REVIEWER" })
    assert.equal(document.querySelectorAll('input[type="checkbox"]').length, 0)
    assert.equal(button("批量通过"), undefined)
    await click(button("批量处理"))
    assert.ok(document.querySelectorAll('input[type="checkbox"]').length > 0)
    assert.equal(button("批量通过").disabled, true)
  })

  await test("退回决定先展开必要表单，确认后才执行原有回调", async () => {
    let returned = 0
    const submission = { ...baseSubmission, status: "BRANCH_REVIEW", level: "BRANCH", can: { review: true } }
    await mount(<ReviewDecisionPanel submission={submission} onReturn={() => { returned += 1 }} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(document.querySelector('input[type="date"]'), null)
    await click(button("退回整改"))
    assert.equal(returned, 0)
    assert.ok(document.querySelector('input[type="date"]'))
    assert.equal(button("确认退回").disabled, true)
    await input(document.querySelector('[aria-label="审核意见"]'), "请补充完整签名后重新提交")
    await click(button("确认退回"))
    assert.equal(returned, 1)
  })

  await test("框选按显示比例保存页码与坐标，单击不创建区域，Esc 取消", async () => {
    const selections = []
    await mount(<MaterialViewer materialId={12} versionId={402} page={2} onSelectRegion={(location) => selections.push(location)} />)
    await click(button("框选新增问题"))
    const area = document.querySelector('[aria-label="框选问题区域"]')
    area.getBoundingClientRect = () => ({ left: 100, top: 50, width: 300, height: 400 })
    const pointer = async (type, x, y) => act(async () => { const event = new MouseEvent(type, { bubbles: true, clientX: x, clientY: y, button: 0 }); Object.defineProperty(event, "pointerId", { value: 1 }); area.dispatchEvent(event) })
    await pointer("pointerdown", 250, 250)
    await pointer("pointerup", 250, 250)
    assert.equal(selections.length, 0)
    await pointer("pointerdown", 250, 250)
    await pointer("pointermove", 130, 90)
    await pointer("pointerup", 130, 90)
    assert.deepEqual(selections[0], { material_id: 12, version_id: 402, page_no: 2, bbox: [59.5, 84.2, 297.5, 421] })
    await click(button("框选新增问题"))
    await act(async () => window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })))
    assert.equal(document.querySelector('[aria-label="框选问题区域"]'), null)
  })

  await test("审核工作区框选后填问题，提交包含精确当前版本与区域", async () => {
    const material = { ...baseMaterial, current_version_id: 402, version_no: 2, page_count: 3 }
    let saved
    await mount(<ReviewWorkspacePage />, { path: "/review/submissions/101", pattern: "/review/submissions/:id", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/submissions/101") return { ...baseSubmission, status: "BRANCH_REVIEW", materials: [material], can: { add_issue: true } }
      if (config.url === "/submissions/101/issues" && config.method === "post") { saved = JSON.parse(config.data); return { id: 60, ...saved } }
    } })
    await click(button("框选新增问题"))
    const area = document.querySelector('[aria-label="框选问题区域"]')
    area.getBoundingClientRect = () => ({ left: 0, top: 0, width: 595, height: 842 })
    for (const [type, x, y] of [["pointerdown", 40, 60], ["pointerup", 200, 100]]) await act(async () => { const event = new MouseEvent(type, { bubbles: true, clientX: x, clientY: y, button: 0 }); Object.defineProperty(event, "pointerId", { value: 1 }); area.dispatchEvent(event) })
    assert.match(text(), /已框选第 1 页区域/)
    await input(document.querySelector('input[placeholder="标题"]'), "落款缺失")
    await input(document.querySelector('textarea[placeholder="问题描述"]'), "请核对落款日期")
    await click(button("保存"))
    assert.deepEqual(saved.location.bbox, [40, 60, 200, 100])
    assert.equal(saved.location.version_id, 402)
    assert.equal(saved.location.page_no, 1)
    assert.equal(saved.material_id, 12)
  })

  await test("新增问题更换材料时清除原框选，防止坐标串用", async () => {
    let saved
    await mount(<AddIssueModal open materials={[{ id: 12, current_version_id: 402 }, { id: 13, current_version_id: 403 }]} initialLocation={{ material_id: 12, version_id: 402, page_no: 1, bbox: [1, 2, 30, 40] }} onClose={() => {}} onCreate={(body) => { saved = body }} />)
    await input(document.querySelector('select option[value="13"]').parentElement, "13")
    assert.doesNotMatch(text(), /已框选/)
    await input(document.querySelector('input[placeholder="标题"]'), "核对")
    await input(document.querySelector('textarea[placeholder="问题描述"]'), "检查另一份材料")
    await click(button("保存"))
    assert.equal(saved.location.bbox, undefined)
    assert.equal(saved.location.version_id, 403)
  })

  await test("节点新增修改删除只提交增量，并要求填写校正原因", async () => {
    let saved
    const parsed = { version_id: 402, extractions: [{ id: 1, node_code: "T02", date: "2026-01-01" }, { id: 2, node_code: "T06", date: "2026-02-01", seq_index: 0 }] }
    await mount(<ParsedTextPanel parsed={parsed} editable onSave={(body) => { saved = body }} />, { roleCode: "BRANCH_REVIEWER" })
    await input(document.querySelector('[aria-label="记录 1 日期"]'), "2026-01-02")
    await click([...document.querySelectorAll("button")].filter((item) => item.textContent === "删除记录")[1])
    await click(button("新增节点记录"))
    await input(document.querySelector('[aria-label="记录 3 节点"]'), "T10")
    await input(document.querySelector('[aria-label="记录 3 日期"]'), "2026-03-01")
    await input(document.querySelector('[aria-label="记录 3 结束日期"]'), "2026-03-03")
    await input(document.querySelector('[aria-label="记录 3 学时"]'), "24")
    await click(button("保存校正"))
    assert.equal(saved, undefined)
    assert.match(text(), /请填写时间节点校正原因/)
    await input(document.querySelector('[aria-label="时间节点校正原因"]'), "已核对原件，修正日期并补录培训")
    await click(button("保存并重新校验"))
    assert.equal(saved.extractions.length, 3)
    assert.deepEqual(saved.extractions[1], { extraction_id: 2, delete: true })
    assert.equal(saved.extractions[2].hours, 24)
    assert.equal(saved.recheck, true)
    assert.match(saved.reason, /核对原件/)
  })

  await test("节点校正失败保留输入，撤销删除后不把未改记录变为人工记录", async () => {
    let saved
    let fail = true
    const parsed = { version_id: 402, extractions: [{ id: 1, node_code: "T02", date: "2026-01-01" }] }
    await mount(<ParsedTextPanel parsed={parsed} editable onSave={(body) => { if (fail) throw new Error("保存连接失败"); saved = body }} />, { roleCode: "BRANCH_REVIEWER" })
    await click(button("删除记录"))
    await click(button("撤销删除"))
    await input(document.querySelector("textarea"), "校正后的全文")
    await click(button("保存校正"))
    assert.match(text(), /保存连接失败/)
    assert.equal(document.querySelector("textarea").value, "校正后的全文")
    fail = false
    await click(button("保存校正"))
    assert.equal(saved.extractions, undefined)
    assert.equal(saved.corrected_text, "校正后的全文")
  })

  await test("学生或历史材料只读面板不提供节点编辑按钮", async () => {
    await mount(<ParsedTextPanel parsed={{ version_id: 401, extractions: [{ id: 1, node_code: "T02", date: "2026-01-01" }] }} editable={false} />)
    assert.equal(button("新增节点记录"), undefined)
    assert.equal(button("删除记录"), undefined)
    assert.equal(requests.some((request) => request.url === "/meta"), false)
    assert.equal(document.querySelector("textarea").readOnly, true)
  })

  // ---- 本轮新增：审核待办改用后端筛选、统一的加载/失败/空状态、懒加载失败、ZIP 导入阶段 ----
  const listRequests = () => requests.filter((request) => request.url === "/submissions")
  const field = (label) => [...document.querySelectorAll("label")].find((node) => node.querySelector("span")?.textContent === label)?.querySelector("select, input")

  await test("待办每次筛选只发一个列表请求，无关键问题与截止参数原样交给后端", async () => {
    // 450 条结果：原先的浏览器端补做筛选需要按每页 200 条拉取 3 次
    const many = (config) => config.url === "/submissions" ? { items: [{ id: 101, student_name: "测试学生", stage_code: 1, status: "BRANCH_REVIEW", issue_counts: {} }], total: 450, page: 1, page_size: 20 } : undefined
    await mount(<ReviewTasksPage />, { path: "/review/tasks?due_within_days=7", roleCode: "BRANCH_REVIEWER", handler: many })
    const before = listRequests().length
    await input(field("关键问题"), "false")
    const sent = listRequests().slice(before)
    assert.equal(sent.length, 1)
    assert.equal(sent[0].params.has_block, "false")
    assert.equal(sent[0].params.due_within_days, "7")
    assert.equal(sent[0].params.todo, "true")
    assert.equal(sent[0].params.page_size, 20)
    assert.match(text(), /共 450 份提交材料/)
  })

  await test("首页“七日内到期”进入时截止筛选可见、可清除，筛选项含“仅看无关键问题”", async () => {
    await mount(<ReviewTasksPage />, { path: "/review/tasks?due_within_days=7", roleCode: "BRANCH_REVIEWER" })
    assert.equal(document.querySelector("details").open, true)
    assert.equal(field("截止").value, "7")
    assert.deepEqual([...field("截止").options].map((option) => option.text), ["全部", "今天到期或已逾期", "3 天内", "7 天内", "14 天内"])
    assert.ok([...field("关键问题").options].some((option) => option.value === "false" && option.text === "仅看无关键问题"))
    await input(field("关键问题"), "false")
    assert.equal(listRequests().at(-1).params.has_block, "false")
    await click(button("重置"))
    const last = listRequests().at(-1).params
    assert.equal(last.due_within_days, undefined)
    assert.equal(last.has_block, undefined)
  })

  await test("待办加载失败只显示错误与重试，不显示空状态，重试后恢复数据", async () => {
    let failing = true
    await mount(<ReviewTasksPage />, { path: "/review/tasks", roleCode: "BRANCH_REVIEWER", handler: (config) => { if (config.url === "/submissions" && failing) throw new Error("待办服务暂不可用") } })
    assert.match(text(), /待办服务暂不可用/)
    assert.equal(document.querySelectorAll('[role="alert"]').length, 1)
    assert.doesNotMatch(text(), /当前层级没有待办|共 0 份/)
    failing = false
    await click(button("重试"))
    assert.match(text(), /测试学生/)
    assert.doesNotMatch(text(), /待办服务暂不可用/)
  })

  await test("待办参数被后端拒绝时指出无效的筛选条件", async () => {
    await mount(<ReviewTasksPage />, { path: "/review/tasks?due_within_days=9999", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/submissions") throw Object.assign(new Error("Request failed with status code 422"), { config, response: { status: 422, headers: {}, data: { code: 42200, message: "参数校验失败", data: { errors: [{ loc: ["query", "due_within_days"], msg: "Input should be less than or equal to 3650" }] } } } })
    } })
    assert.match(text(), /参数校验失败：截止天数的取值无效/)
    assert.equal(field("截止").value, "9999")
    assert.ok(button("重试"))
  })

  await test("待办为空时按是否筛选显示对应提示，可一键清除筛选", async () => {
    const none = (config) => config.url === "/submissions" ? { items: [], total: 0, page: 1, page_size: 20 } : undefined
    await mount(<ReviewTasksPage />, { path: "/review/tasks", roleCode: "BRANCH_REVIEWER", handler: none })
    assert.match(text(), /当前层级没有待办/)
    await mount(<ReviewTasksPage />, { path: "/review/tasks?has_block=false", roleCode: "BRANCH_REVIEWER", handler: none })
    assert.match(text(), /没有符合筛选条件的提交包/)
    await click(button("清除筛选条件"))
    assert.equal(listRequests().at(-1).params.has_block, undefined)
  })

  await test("批量通过按统一口径提示，结果逐项显示后端原因", async () => {
    await mount(<ReviewTasksPage />, { path: "/review/tasks", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/submissions/batch-review") return { passed: [], failed: [{ submission_id: 101, code: 40903, reason: "仍有未处理的关键问题" }] }
    } })
    await click(button("批量处理"))
    assert.match(text(), /已确认、修改或驳回的关键问题不拦截，单份与批量一致/)
    await click(document.querySelector('input[aria-label="选择行"]'))
    await click(button("批量通过"))
    assert.match(text(), /按单份通过的同一套规则/)
    await click(button("确认批量通过"))
    const body = JSON.parse(requests.find((request) => request.url === "/submissions/batch-review").data)
    assert.deepEqual(body.submission_ids, [101])
    assert.match(text(), /未通过 1 份/)
    assert.match(text(), /提交包 #101：仍有未处理的关键问题/)
  })

  await test("审核面板的通过规则说明与批量一致，不再提示批量会拒绝", async () => {
    const submission = { ...baseSubmission, status: "BRANCH_REVIEW", level: "BRANCH", can: { review: true } }
    await mount(<ReviewDecisionPanel submission={submission} issues={[{ id: 51, severity: "BLOCK", is_active: true, review_status: "CONFIRMED", report_id: 201 }]} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("通过")?.disabled, false)
    assert.match(text(), /已确认、修改或驳回的关键问题不拦截，单份与批量一致/)
    assert.doesNotMatch(text(), /批量通过会拒绝/)
  })

  await test("审计日志加载失败可重试，ZIP 导入动作显示中文名", async () => {
    let failing = true
    await mount(<AuditLogsPage />, { path: "/admin/audit-logs", roleCode: "ORG_ADMIN", handler: (config) => {
      if (config.url !== "/audit-logs") return undefined
      if (failing) throw new Error("审计服务暂不可用")
      return { items: [{ id: 1, created_at: "2026-10-23T10:00:00+08:00", username: "reviewer", role: "BRANCH_REVIEWER", action: "BATCH_IMPORT", object_type: "material", object_id: 90, detail: { job_id: 501 } }], total: 1, page: 1, page_size: 20 }
    } })
    assert.match(text(), /审计服务暂不可用/)
    assert.doesNotMatch(text(), /没有符合条件的审计记录/)
    failing = false
    await click(button("重试"))
    assert.match(text(), /批量导入材料/)
  })

  await test("任务明细加载失败在明细区提示，重试后显示任务进度", async () => {
    let attempts = 0
    await mount(<JobsPage />, { path: "/tasks/jobs?view=all", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/jobs") return { items: [{ id: 7, job_type: "BATCH_UPLOAD", status: "SUCCEEDED", total: 2, done_count: 2 }], total: 1, page: 1, page_size: 20 }
      if (config.url === "/jobs/7") {
        if (++attempts === 1) throw new Error("任务服务暂不可用")
        return { id: 7, job_type: "BATCH_UPLOAD", status: "SUCCEEDED", total: 2, done_count: 2, result: { imported: 2 } }
      }
    } })
    await click(button("批量上传"))
    assert.match(text(), /任务明细加载失败/)
    assert.match(text(), /任务服务暂不可用/)
    await click(button("重试"))
    assert.match(text(), /批量上传 · 已完成/)
  })

  await test("页面文件下载失败时自动重试一次，仍失败显示中文错误页与重新加载", async () => {
    let downloads = 0
    const Broken = lazyWithRetry(() => { downloads += 1; return Promise.reject(new TypeError("Failed to fetch dynamically imported module: /assets/Page-old.js")) }, { delay: 0 })
    // React 与 React Router 会把被错误边界接住的错误打印到控制台，这里是预期的，暂时静音
    const consoleError = console.error
    console.error = () => {}
    try {
      await mount(null, { routes: [{ path: "/", element: <React.Suspense fallback={<p>加载中</p>}><Broken /></React.Suspense>, errorElement: <RouteError fullPage /> }] })
      await flush()
    } finally { console.error = consoleError }
    assert.equal(downloads, 2)
    assert.match(text(), /页面文件下载失败/)
    assert.match(text(), /登录状态不受影响/)
    assert.ok(button("重新加载"))
    assert.doesNotMatch(text(), /Unexpected Application Error/)
  })

  await test("外壳内的页面都已登记在外壳块的导入清单中", async () => {
    assert.equal(shellPageNames.size, 33)
    for (const name of shellPageNames) assert.equal(typeof shellPages[name], "function", name)
  })

  await test("ZIP 确认携带导入阶段，结果区分本次导入与此前已入库", async () => {
    const items = [{ item_id: 31, entry_path: "20260001_申请书.pdf", status: "MATCHED", matched_archive: { id: 1, real_name: "测试学生" } }]
    await mount(<BatchUploadPage />, { path: "/materials/batch-upload", roleCode: "BRANCH_REVIEWER", handler: (config) => {
      if (config.url === "/materials/batch-upload") return { job_id: 601 }
      if (config.url === "/jobs/601") return { id: 601, status: "SUCCEEDED", params: { stage_code: 2 }, result: { items } }
      if (config.url === "/materials/batch-upload/601/assign") return { imported: 0, already_imported: 1, skipped: 0, failed: 0, items: [{ ...items[0], status: "IMPORTED", material_id: 77, stage_code: 2, already_imported: true, note: "相同文件已在该提交包中，未重复入库" }] }
    } })
    await input(document.querySelector('[aria-label="发展阶段"]'), "2")
    const fileInput = document.querySelector('input[type="file"]')
    await act(async () => { Object.defineProperty(fileInput, "files", { value: [new File(["ZIP"], "samples.zip")] }); fileInput.dispatchEvent(new Event("change", { bubbles: true })); await wait() })
    await flush()
    assert.equal(requests.find((request) => request.url === "/materials/batch-upload").data.get("stage_code"), "2")
    assert.equal(document.querySelector('[aria-label="导入阶段"]').value, "2")
    await click(button("确认导入 1 个文件"))
    const body = JSON.parse(requests.find((request) => request.url.endsWith("/assign")).data)
    assert.equal(body.stage_code, 2)
    assert.match(text(), /本次导入 0 个 · 此前已入库 1 个/)
    assert.match(text(), /相同文件已在该提交包中，未重复入库/)
  })

  if (root) await act(async () => root.unmount())
  router?.dispose()
  tokenStore.clear()
  return results
}
