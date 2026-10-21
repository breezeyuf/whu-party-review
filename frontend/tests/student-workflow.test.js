import assert from "node:assert/strict"
import { test } from "node:test"
import { pendingParseCount, pendingStudentReplies, studentSubmitReason } from "../src/utils/studentWorkflow.js"

const draft = { status: "DRAFT", ai_status: "DONE", can: { submit: true }, latest_report: { id: 1, is_stale: false } }

test("initial submission requires a current report and replies to non-rejected blocking issues", () => {
  assert.equal(studentSubmitReason(draft, []), "")
  assert.match(studentSubmitReason({ ...draft, latest_report: null }, []), /自查/)
  assert.match(studentSubmitReason({ ...draft, latest_report: { is_stale: true } }, []), /重新自查/)
  const issues = [
    { id: 1, severity: "BLOCK", review_status: "PENDING" },
    { id: 2, severity: "BLOCK", review_status: "REJECTED" },
    { id: 3, severity: "WARN", review_status: "CONFIRMED" },
    { id: 4, severity: "BLOCK", review_status: "CONFIRMED", response_type: "EXPLAINED" },
  ]
  assert.deepEqual(pendingStudentReplies(draft, issues).map((issue) => issue.id), [1])
  assert.match(studentSubmitReason(draft, issues), /1 条阻断问题/)
})

test("resubmission permits a stale report and requires all confirmed issues regardless of severity", () => {
  const returned = { ...draft, status: "RETURNED", latest_report: { is_stale: true } }
  assert.equal(studentSubmitReason(returned, []), "")
  const issues = [
    { id: 1, severity: "INFO", review_status: "CONFIRMED" },
    { id: 2, severity: "WARN", review_status: "MODIFIED" },
    { id: 3, severity: "BLOCK", review_status: "PENDING" },
    { id: 4, severity: "BLOCK", review_status: "CONFIRMED", is_active: false },
    { id: 5, severity: "BLOCK", review_status: "CONFIRMED", response_type: "MODIFIED" },
  ]
  assert.deepEqual(pendingStudentReplies(returned, issues).map((issue) => issue.id), [1, 2])
  assert.match(studentSubmitReason(returned, issues), /2 条已确认问题/)
})

test("permissions, unfinished jobs, and unavailable issue data prevent submit", () => {
  assert.match(studentSubmitReason({ ...draft, can: { submit: false } }, []), /不可提交/)
  assert.match(studentSubmitReason(draft, [], { ready: false }), /读取/)
  assert.match(studentSubmitReason(draft, [], { taskPending: true }), /任务/)
  assert.match(studentSubmitReason({ ...draft, ai_status: "RUNNING" }, []), /任务/)
  assert.match(studentSubmitReason({ ...draft, ai_status: "FAILED" }, []), /自查/)
})

test("parsing checks cover checklist, extra, and unclassified materials without double counting", () => {
  const pending = { id: 1, current_version: { parse_status: "PENDING" } }
  assert.equal(pendingParseCount([{
    checklist: [{ materials: [pending, { id: 2, current_version: { parse_status: "DONE" } }] }],
    unclassified: [pending, { id: 3, current_version: { parse_status: "RUNNING" } }],
    extra: [{ id: 4, current_version: { parse_status: "FAILED" } }],
  }]), 2)
})
