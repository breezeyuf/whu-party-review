import test from "node:test"
import assert from "node:assert/strict"
import { nextStudentAction, isMenuActive, countActiveFilters } from "../src/utils/workbench.js"
import { menusFor } from "../src/utils/permissions.js"

test("学生首页按实际状态引导材料、提交、整改和等待审核", () => {
  const draft = { id: 10, status: "DRAFT" }
  assert.equal(nextStudentAction(draft, null).to, "/my/materials")
  assert.equal(nextStudentAction(draft, { actual: 1, expected: 2 }).to, "/my/materials")
  assert.equal(nextStudentAction(draft, { actual: 2, expected: 2 }).to, "/my/self-check/10")
  assert.equal(nextStudentAction({ ...draft, status: "RETURNED" }, null).to, "/my/rectification")
  assert.equal(nextStudentAction({ ...draft, status: "BRANCH_REVIEW" }, null).to, "/my/progress")
  assert.equal(nextStudentAction({ ...draft, status: "FILED" }, null).step, 3)
  assert.equal(nextStudentAction(draft, { actual: 0, expected: 0 }).to, "/my/materials")
})

test("常用菜单精简后所有有权使用的功能仍可到达", () => {
  const reviewer = menusFor({ role: "BRANCH_REVIEWER" })
  assert.deepEqual(reviewer.filter((group) => !group.collapsible).flatMap((group) => group.items.map((item) => item.to)), ["/", "/review/tasks", "/archives", "/messages"])
  const routes = reviewer.flatMap((group) => group.items.map((item) => item.to))
  for (const route of ["/materials/batch-upload", "/notices", "/tasks/jobs", "/rules/time-rules", "/stats/overview"]) assert.ok(routes.includes(route))
  const rulesGroup = reviewer.find((group) => group.group === "材料与审核标准")
  assert.deepEqual(rulesGroup.items.map((item) => item.label), ["材料标准", "审核规则", "规则治理"])
  assert.ok(rulesGroup.items.some((item) => item.activePaths?.includes("/rules/material-types")))
  for (const route of ["/admin/users", "/admin/settings", "/cross-review"]) assert.ok(!routes.includes(route))
  const crossRoutes = menusFor({ role: "CROSS_REVIEWER" }).flatMap((group) => group.items.map((item) => item.to))
  assert.ok(!crossRoutes.includes("/materials/batch-upload"))
  assert.equal(menusFor({ role: "STUDENT" }).flatMap((group) => group.items).length, 5)
})

test("菜单分组正确识别嵌套路径而不误匹配相似地址", () => {
  assert.equal(isMenuActive("/", "/"), true)
  assert.equal(isMenuActive("/archives/12", "/"), false)
  assert.equal(isMenuActive("/archives/12", "/archives"), true)
  assert.equal(isMenuActive("/archives-other", "/archives"), false)
  assert.equal(isMenuActive("/review/submissions/101", "/review/tasks"), true)
})

test("已启用的否定筛选仍计入可见提示", () => {
  assert.equal(countActiveFilters({ has_block: "false", status: "", due: 0 }, ["has_block", "status", "due"]), 2)
})
