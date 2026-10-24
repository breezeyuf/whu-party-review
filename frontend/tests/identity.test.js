import test from "node:test"
import assert from "node:assert/strict"
import { activeOrganization, identityFor, loginDestination, roleKey } from "../src/utils/identity.js"
import { can, menusFor } from "../src/utils/permissions.js"
import { isMenuActive } from "../src/utils/workbench.js"

test("身份首页覆盖学生、审核和两类管理员，未知身份不进入业务", () => {
  for (const [role, home] of [["STUDENT", "/student"], ["BRANCH_REVIEWER", "/review"], ["CROSS_REVIEWER", "/review"], ["COLLEGE_REVIEWER", "/review"], ["SYS_ADMIN", "/admin"], ["ORG_ADMIN", "/admin"]]) {
    assert.equal(loginDestination({ active_role: { role } }), home)
    assert.equal(isMenuActive(home, "/"), true)
  }
  for (const role of ["UNKNOWN", "toString", "__proto__"]) assert.equal(identityFor({ role }), null)
  assert.equal(loginDestination({ active_role: { role: "UNKNOWN" } }), "/choose-identity")
})

test("改密优先于身份选择，多组织的同名角色有不同身份键", () => {
  assert.equal(loginDestination({ must_change_password: true }, true), "/change-password")
  assert.equal(loginDestination({ active_role: { role: "STUDENT" } }, true), "/choose-identity")
  assert.notEqual(roleKey({ role: "BRANCH_REVIEWER", org_id: 1 }), roleKey({ role: "BRANCH_REVIEWER", org_id: 2 }))
})

test("学生无任何管理或审核菜单，管理员无学生专属页面权限", () => {
  const student = { role: "STUDENT" }
  for (const key of ["review", "archives", "users", "orgs", "settings", "audit", "rulesRead", "stats"]) assert.equal(can(student, key), false)
  assert.equal(can(student, "student"), true)
  assert.equal(can(student, "materialRead"), true)
  for (const role of ["SYS_ADMIN", "ORG_ADMIN", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER"]) {
    assert.equal(can({ role }, "student"), false)
    assert.ok(!menusFor({ role }).flatMap((g) => g.items).some((item) => item.to.startsWith("/my/")))
  }
})

test("管理员直接看到管理菜单，组织管理员保留备案与档案权限", () => {
  for (const role of ["SYS_ADMIN", "ORG_ADMIN"]) {
    const admin = menusFor({ role }).find((group) => group.group === "组织与系统管理")
    assert.equal(admin.collapsible, false)
    assert.ok(admin.items.some((item) => item.to === "/admin/users"))
  }
  assert.equal(can({ role: "ORG_ADMIN" }, "review"), true)
  assert.equal(can({ role: "ORG_ADMIN" }, "archives"), true)
  assert.equal(can({ role: "SYS_ADMIN" }, "review"), false)
})

test("组织名称跟随当前身份的组织范围，不沿用账号默认组织", () => {
  const active_role = { role: "BRANCH_REVIEWER", org_id: 3 }
  assert.equal(activeOrganization({ active_role, org_name: "账号默认组织", roles: [{ role: "BRANCH_REVIEWER", org_id: 2, org_name: "原组织" }, { ...active_role, org_name: "当前审核组织" }] }), "当前审核组织")
  assert.equal(activeOrganization({ org_name: "账号默认组织" }), "账号默认组织")
})
