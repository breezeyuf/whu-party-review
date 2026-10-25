import React, { act } from "react"
import { createRoot } from "react-dom/client"
import { createMemoryRouter, RouterProvider } from "react-router-dom"
import assert from "node:assert/strict"
import { api, tokenStore } from "../src/api/client"
import { AuthProvider } from "../src/context/AuthContext"
import { ToastProvider } from "../src/context/ToastContext"
import ArchiveListPage from "../src/pages/archive/ArchiveListPage"
import UsersPage from "../src/pages/admin/UsersPage"
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
import OcrStatusPanel from "../src/components/common/OcrStatusPanel"
import AddIssueModal from "../src/components/review/AddIssueModal"
import ReviewWorkspacePage from "../src/pages/review/ReviewWorkspacePage"
import IssueResponseForm from "../src/components/student/IssueResponseForm"
import ReviewJobStatus from "../src/components/review/ReviewJobStatus"
import { StudentDashboard, ReviewerDashboard } from "../src/pages/dashboard/Dashboards"
import AppLayout from "../src/components/layout/AppLayout"
import FilterBar from "../src/components/common/FilterBar"
import ReviewTasksPage from "../src/pages/review/ReviewTasksPage"
import CrossReviewConfigPage from "../src/pages/review/CrossReviewConfigPage"
import AuditLogsPage from "../src/pages/admin/AuditLogsPage"
import JobsPage from "../src/pages/review/JobsPage"
import RouteError from "../src/components/common/RouteError"
import { lazyWithRetry } from "../src/utils/lazyLoad"
import { pages as shellPages } from "../src/components/layout/shellModule"
import { shellPageNames } from "../src/components/layout/lazyShell"
import "../src/routes"

const wait = (ms = 15) => new Promise((resolve) => setTimeout(resolve, ms))
const flush = () => act(async () => { await wait(); await wait() })
const baseReport = { id: 201, status: "DONE", is_stale: false, summary: {}, handover_status: "NOT_REQUIRED", recommendation: "PASS" }
const baseArchive = { id: 1, real_name: "测试学生", student_no: "20260001", current_stage: 1, status: "ACTIVE", submissions: [], current_submission: { id: 101, status: "DRAFT" } }
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
  if (url === "/rules/time-nodes") return nodeDefinitions
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

  await test("OCR 自检等待真实识别，禁止重复点击并显示识别文本", async () => {
    let finish
    await mount(<OcrStatusPanel settings={{ available_engines: ["paddleocr"] }} />, { handler: (config) => {
      if (config.url === "/settings/ai/test") return new Promise((resolve) => { finish = resolve })
    } })
    assert.match(text(), /已安装引擎 paddleocr/)
    await click(button("测试 OCR"))
    assert.equal(button("正在加载模型并识别…").disabled, true)
    assert.equal(requests.filter((item) => item.url === "/settings/ai/test").length, 1)
    await act(async () => finish({ ok: true, recognized_text: "OCR 12345", latency_ms: 120, message: "识别成功" }))
    await flush()
    assert.match(text(), /识别自检通过/)
    assert.match(text(), /OCR 12345/)
  })

  await test("OCR 自检异常可见并允许再次测试", async () => {
    await mount(<OcrStatusPanel />, { handler: (config) => {
      if (config.url === "/settings/ai/test") throw new Error("模型不可用")
    } })
    await click(button("测试 OCR"))
    assert.match(text(), /识别自检失败.*模型不可用/)
    assert.equal(button("测试 OCR").disabled, false)
  })

  await test("OCR 中文结果与警告在解析面板中展示", async () => {
    await mount(<ParsedTextPanel parsed={{ parser: "OCR", ocr_engine: "paddleocr", page_count: 1,
      full_text: "入党申请书 测试材料 OCR 20260001", warnings: ["印章和手写签名需人工复核"], extracted_fields: {} }} editable={false} />)
    assert.match(text(), /OCR paddleocr/)
    assert.match(text(), /印章和手写签名需人工复核/)
    assert.match(document.querySelector("textarea").value, /申请书.*20260001/)
  })

  await test("当前失败版本可重试解析并进入任务轮询", async () => {
    let retried = false
    await mount(<MaterialDetailPage />, { path: "/materials/12", pattern: "/materials/:id", handler: (config) => {
      const version = { ...currentVersion, parse_status: retried ? "PENDING" : "FAILED", parse_error: "OCR 识别失败" }
      if (config.url === "/materials/12") return { ...baseMaterial, current_version: version }
      if (config.url === "/materials/12/versions") return [version]
      if (config.url === "/submissions/101") return { ...baseSubmission, can: { upload: true } }
      if (config.url === "/materials/12/retry-parse") { retried = true; return { parse_job_id: 789 } }
      if (config.url === "/jobs/789") return { id: 789, job_type: "PARSE", status: "RUNNING", progress: 10 }
    } })
    await click(button("重试解析"))
    assert.ok(requests.some((item) => item.url === "/materials/12/retry-parse"))
    assert.ok(requests.some((item) => item.url === "/jobs/789"))
    assert.match(text(), /正在解析/)
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
      const picker = document.querySelectorAll('input[type="file"]')[1]
      Object.defineProperty(picker, "files", { value: [new File(["synthetic"], "users.xlsx")], configurable: true })
      await act(async () => picker.dispatchEvent(new Event("change", { bubbles: true })))
      await flush()
      await click(button("确认并导入"))
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

  await test("学生发展进度页正常加载时间节点与审核轨迹，且不重复展示", async () => {
    await mount(<MyProgressPage />, {
      path: "/my/progress",
      handler: (config) => {
        if (config.url === "/archives/1/history") return [{ time: "2026-10-20T10:00:00", kind: "REVIEW", title: "PASS", detail: "审核通过", actor_name: "审核员", link_type: "submission", link_id: 101 }]
        if (config.url === "/archives/1/timeline") return { stages: [], nodes: [{ code: "N1", name: "递交入党申请", effective: { date: "2025-10-10" }, sources: [] }], derived: [] }
        return undefined
      },
    })
    assert.match(text(), /审核轨迹/)
    assert.match(text(), /审核通过/)
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

  await test("待确认阻断问题禁止通过，驳回后可通过", async () => {
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
    await click(button("规则库"))
    assert.equal(visibleLinks().length, 12)
    assert.equal(button("规则库").getAttribute("aria-expanded"), "true")
  })

  await test("访问低频功能时对应菜单自动展开", async () => {
    await mount(<AppLayout><p>时间规则</p></AppLayout>, { path: "/rules/time-rules", roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("规则库").getAttribute("aria-expanded"), "true")
    assert.equal(document.querySelector('a[href="/rules/time-rules"]').closest("ul").hidden, false)
  })

  await test("学生首页主入口会随退回状态指向整改", async () => {
    await mount(<StudentDashboard data={{ archive_id: 1, submission: { id: 101, status: "RETURNED" } }} />)
    const primary = document.querySelector(".next-action .btn-primary")
    assert.equal(primary.getAttribute("href"), "/my/rectification")
    assert.equal(document.querySelectorAll(".next-action .btn-primary").length, 1)
  })

  await test("高级筛选默认收起，但启用的筛选条件会显示数量并展开", async () => {
    const props = { fields: [{ key: "q", label: "姓名" }], advancedFields: [{ key: "has_block", label: "有无阻断" }], onChange: () => {} }
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
    assert.equal(requests.some((request) => request.url === "/rules/time-nodes"), false)
    assert.equal(document.querySelector("textarea").readOnly, true)
  })

  // ---- 本轮新增：审核待办改用后端筛选、统一的加载/失败/空状态、懒加载失败、ZIP 导入阶段 ----
  const listRequests = () => requests.filter((request) => request.url === "/submissions")
  const field = (label) => [...document.querySelectorAll("label")].find((node) => node.querySelector("span")?.textContent === label)?.querySelector("select, input")

  await test("待办每次筛选只发一个列表请求，无阻断与截止参数原样交给后端", async () => {
    // 450 条结果：原先的浏览器端补做筛选需要按每页 200 条拉取 3 次
    const many = (config) => config.url === "/submissions" ? { items: [{ id: 101, student_name: "测试学生", stage_code: 1, status: "BRANCH_REVIEW", issue_counts: {} }], total: 450, page: 1, page_size: 20 } : undefined
    await mount(<ReviewTasksPage />, { path: "/review/tasks?due_within_days=7", roleCode: "BRANCH_REVIEWER", handler: many })
    const before = listRequests().length
    await input(field("阻断问题"), "false")
    const sent = listRequests().slice(before)
    assert.equal(sent.length, 1)
    assert.equal(sent[0].params.has_block, "false")
    assert.equal(sent[0].params.due_within_days, "7")
    assert.equal(sent[0].params.todo, "true")
    assert.equal(sent[0].params.page_size, 20)
    assert.match(text(), /共 450 份提交材料/)
  })

  await test("首页“七日内到期”进入时截止筛选可见、可清除，筛选项含“仅看无阻断”", async () => {
    await mount(<ReviewTasksPage />, { path: "/review/tasks?due_within_days=7", roleCode: "BRANCH_REVIEWER" })
    assert.equal(document.querySelector("details").open, true)
    assert.equal(field("截止").value, "7")
    assert.deepEqual([...field("截止").options].map((option) => option.text), ["全部", "今天到期或已逾期", "3 天内", "7 天内", "14 天内"])
    assert.ok([...field("阻断问题").options].some((option) => option.value === "false" && option.text === "仅看无阻断"))
    await input(field("阻断问题"), "false")
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
      if (config.url === "/submissions/batch-review") return { passed: [], failed: [{ submission_id: 101, code: 40903, reason: "仍有未处理的阻断问题" }] }
    } })
    await click(button("批量处理"))
    assert.match(text(), /已确认、修改或驳回的阻断问题不拦截，单份与批量一致/)
    await click(document.querySelector('input[aria-label="选择行"]'))
    await click(button("批量通过"))
    assert.match(text(), /按单份通过的同一套规则/)
    await click(button("确认批量通过"))
    const body = JSON.parse(requests.find((request) => request.url === "/submissions/batch-review").data)
    assert.deepEqual(body.submission_ids, [101])
    assert.match(text(), /未通过 1 份/)
    assert.match(text(), /提交包 #101：仍有未处理的阻断问题/)
  })

  await test("审核面板的通过规则说明与批量一致，不再提示批量会拒绝", async () => {
    const submission = { ...baseSubmission, status: "BRANCH_REVIEW", level: "BRANCH", can: { review: true } }
    await mount(<ReviewDecisionPanel submission={submission} issues={[{ id: 51, severity: "BLOCK", is_active: true, review_status: "CONFIRMED", report_id: 201 }]} />, { roleCode: "BRANCH_REVIEWER" })
    assert.equal(button("通过")?.disabled, false)
    assert.match(text(), /已确认、修改或驳回的阻断问题不拦截，单份与批量一致/)
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
    await mount(<JobsPage />, { path: "/tasks/jobs", roleCode: "BRANCH_REVIEWER", handler: (config) => {
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
    assert.equal(shellPageNames.size, 32)
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
