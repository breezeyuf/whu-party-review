import test from "node:test"
import assert from "node:assert/strict"
import { batchReviewResult, issueHighlights, issueLocation, loadAllReviewIssues, loadReviewTasks, passBlockReason, reportBlockReason, reviewHistoryLink } from "../src/utils/review.js"

const current = () => ({ ai_status: "DONE", latest_report: { id: 7, is_stale: false, handover_status: "NOT_REQUIRED" } })

test("no-block and due filters inspect every server page before calculating totals and paging", async () => {
  const calls = []
  const pages = [
    [{ id: 1, issue_counts: { BLOCK: 1 }, days_left: 1 }, { id: 2, issue_counts: { BLOCK: 0 }, days_left: 8 }],
    [{ id: 3, issue_counts: { BLOCK: 0 }, days_left: -2 }, { id: 4, issue_counts: { BLOCK: 0 }, days_left: 2 }],
    [{ id: 5, issue_counts: { BLOCK: 0 }, days_left: null }],
  ]
  const result = await loadReviewTasks(async (params) => {
    calls.push(params)
    return { items: pages[params.page - 1], total: 5, page_size: 2, page: params.page }
  }, { page: 2, page_size: 1, has_block: "false", due_within_days: "3", todo: "false", q: "李" })
  assert.equal(result.total, 2)
  assert.equal(result.page, 2)
  assert.deepEqual(result.items.map((r) => r.id), [4])
  assert.equal(calls.length, 3)
  assert.ok(calls.every((params) => params.has_block == null && params.due_within_days == null && params.q === "李" && params.todo === "false"))
})

test("due=0 includes overdue and today, excluding unset deadlines", async () => {
  const result = await loadReviewTasks(async () => ({ items: [{ days_left: -1 }, { days_left: 0 }, { days_left: 1 }, { days_left: null }], total: 4 }), { due_within_days: "0" })
  assert.deepEqual(result.items.map((r) => r.days_left), [-1, 0])
})

test("server-supported filtering and sorting preserve normal server pagination", async () => {
  const query = { page: 3, has_block: "true", sort: "-issue_count" }
  let seen
  const expected = { items: [{ id: 8 }], total: 50, page: 3, page_size: 20 }
  const result = await loadReviewTasks(async (params) => { seen = params; return expected }, query)
  assert.equal(seen, query)
  assert.equal(result, expected)
})

test("invalid due values cannot silently produce unfiltered results", async () => {
  for (const due of ["-1", "2.5", "abc"]) {
    await assert.rejects(() => loadReviewTasks(() => { throw new Error("should not fetch") }, { due_within_days: due }), /截止天数/)
  }
})

test("incomplete fallback fetches fail visibly instead of under-counting", async () => {
  await assert.rejects(() => loadReviewTasks(async ({ page }) => ({ items: page === 1 ? [{ id: 1 }] : [], total: 3, page_size: 1 }), { has_block: "false" }), /未完整加载/)
})

test("issue loading supports the current unpaginated API and paginated deployments", async () => {
  const all = Array.from({ length: 41 }, (_, i) => ({ id: i + 1 }))
  const result = await loadAllReviewIssues(async () => ({ items: all, counts: { pending_block: 1 } }))
  assert.equal(result.items.length, 41)
  const pages = await loadAllReviewIssues(async ({ page }) => ({ items: all.slice((page - 1) * 20, page * 20), total: 41, page_size: 20 }))
  assert.deepEqual(pages.items, all)
  await assert.rejects(() => loadAllReviewIssues(async ({ page }) => ({ items: page === 1 ? [{ id: 1 }] : [], total: 2, page_size: 1 })), /未完整加载/)
})

test("report gate distinguishes failure, ongoing jobs, missing report and stale report", () => {
  assert.match(reportBlockReason({ ai_status: "FAILED" }), /失败/)
  assert.match(reportBlockReason({ ai_status: "QUEUED" }), /排队/)
  assert.match(reportBlockReason({ ai_status: "RUNNING" }), /运行/)
  assert.match(reportBlockReason({ ai_status: "NONE" }), /没有 AI 报告/)
  const stale = current(); stale.latest_report.is_stale = true
  assert.match(reportBlockReason(stale), /过期/)
  assert.equal(reportBlockReason(current()), "")
})

test("pass and filing remain disabled until all issues and handover are ready", () => {
  assert.match(passBlockReason(current(), [], false), /未完整加载/)
  assert.match(passBlockReason(current(), [{ severity: "BLOCK", review_status: "PENDING" }]), /阻断/)
  const handover = current(); handover.latest_report.handover_status = "REQUIRED"
  assert.match(passBlockReason(handover, []), /接管/)
  handover.latest_report.handover_status = "DONE"
  assert.match(passBlockReason(handover, []), /结论未完成/)
  handover.latest_report.effective_recommendation = "SUGGEST_PASS"
  assert.equal(passBlockReason(handover, []), "")
})

test("individual pass follows backend semantics for manually handled and inactive blockers", () => {
  assert.equal(passBlockReason(current(), [{ severity: "BLOCK", review_status: "REJECTED" }]), "")
  assert.equal(passBlockReason(current(), [{ severity: "BLOCK", review_status: "CONFIRMED" }]), "")
  assert.equal(passBlockReason(current(), [{ severity: "BLOCK", review_status: "PENDING", is_active: false }]), "")
})

test("issue location prefers the checked version and resets unspecified page to 1", () => {
  assert.deepEqual(issueLocation({ material_id: 3, material_version_id: 9, location: { page_no: 4 } }, { current_version_id: 12 }), { materialId: 3, versionId: 9, page: 4 })
  assert.deepEqual(issueLocation({ location: { material_id: "3", version_id: 8 } }, { current_version_id: 12 }), { materialId: "3", versionId: 8, page: 1 })
  assert.equal(issueLocation({ material_id: 3 }, { current_version_id: 12 }).versionId, 12)
})

test("highlights never bleed into another material or another version", () => {
  const material = { id: 3, current_version_id: 12 }
  const issues = [
    { id: 1, material_id: "3", material_version_id: "9", location: { page_no: 2, bbox: [1, 2, 3, 4] } },
    { id: 2, material_id: 3, material_version_id: 12, location: { page_no: 2 } },
    { id: 3, material_id: 4, material_version_id: 9, location: { page_no: 2 } },
    { id: 4, location: { page_no: 2, bbox: [1, 2, 3, 4] } },
    { id: 5, material_id: 3, location: { version_id: 9, page_no: 2 } },
  ]
  assert.deepEqual(issueHighlights(issues, material, 9).map((i) => i.id), [1, 5])
  assert.deepEqual(issueHighlights(issues, material, 12).map((i) => i.id), [2])
  assert.deepEqual(issueHighlights(issues, null, 9), [])
})

test("batch review retains failed and unacknowledged IDs for review, including mixed ID types", () => {
  const result = batchReviewResult([1, 2, 3], { passed: ["1"], failed: [{ submission_id: 2, reason: "报告已过期" }] })
  assert.equal(result.passed, 1)
  assert.deepEqual(result.remaining, [2, 3])
  assert.equal(result.failures[0].reason, "报告已过期")
  assert.match(result.failures[1].reason, /未返回处理结果/)
})

test("history destinations use registered routes and student-accessible submission pages", () => {
  assert.equal(reviewHistoryLink({ link_type: "material", link_id: 2 }, "STUDENT").to, "/materials/2")
  assert.equal(reviewHistoryLink({ link_type: "submission", link_id: 3 }, "STUDENT").to, "/my/self-check/3")
  assert.equal(reviewHistoryLink({ link_type: "submission", link_id: 3 }, "COLLEGE_REVIEWER").to, "/review/submissions/3")
  assert.equal(reviewHistoryLink({ link_type: "notice", link_id: 5 }, "BRANCH_REVIEWER").to, "/notices?notice=5")
  assert.equal(reviewHistoryLink({}, "STUDENT"), null)
})
