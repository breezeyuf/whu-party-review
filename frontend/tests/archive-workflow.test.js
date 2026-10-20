import test from "node:test"
import assert from "node:assert/strict"
import { availableBranches, canManageArchive, checklistProgress, timelineSourceLink } from "../src/utils/archiveWorkflow.js"

const orgs = [
  { id: 1, org_type: "COLLEGE" },
  { id: 2, parent_id: 1, org_type: "BRANCH" },
  { id: 3, parent_id: 4, org_type: "BRANCH" },
  { id: 5, parent_id: 1, org_type: "BRANCH", is_active: false },
]

test("档案创建仅向当前可管理的支部开放", () => {
  assert.deepEqual(availableBranches(orgs, { role: "BRANCH_REVIEWER", org_id: 2 }).map((x) => x.id), [2])
  assert.deepEqual(availableBranches(orgs, { role: "COLLEGE_REVIEWER", org_id: 1 }).map((x) => x.id), [2])
  assert.deepEqual(availableBranches(orgs, { role: "ORG_ADMIN" }).map((x) => x.id), [2, 3])
  for (const role of ["CROSS_REVIEWER", "STUDENT", "SYS_ADMIN"]) {
    assert.equal(canManageArchive({ role }), false)
    assert.deepEqual(availableBranches(orgs, { role }), [])
  }
})

test("真实清单进度不会由额外交件掩盖其他必需材料缺失", () => {
  assert.equal(checklistProgress(null), null)
  assert.deepEqual(checklistProgress({ items: [
    { required: true, expected: 1, actual: 3 },
    { required: true, expected: 2, actual: 0 },
    { required: false, expected: 5, actual: 5 },
  ] }), { expected: 3, actual: 1 })
})

test("时间轴来源跳转保留原始版本号、页码与坐标", () => {
  const url = new URL(timelineSourceLink({ material_id: 12, version_no: 2, page_no: 3, bbox: [10, 20, 30, 40] }), "http://localhost")
  assert.equal(url.pathname, "/materials/12")
  assert.equal(url.searchParams.get("version_no"), "2")
  assert.equal(url.searchParams.get("page"), "3")
  assert.deepEqual(JSON.parse(url.searchParams.get("bbox")), [10, 20, 30, 40])
  assert.equal(url.searchParams.has("version_id"), false)
  assert.equal(timelineSourceLink({}), null)
})
