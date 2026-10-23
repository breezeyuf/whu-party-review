import test from "node:test"
import assert from "node:assert/strict"
import { batchAssignmentBody, materialFocus, mergeBatchItems, positiveInteger, validBbox } from "../src/utils/materialWorkflow.js"

test("issue deep links select the original version, page and bounding box", () => {
  assert.deepEqual(materialFocus({
    issue: { material_version_id: 11, location: { page_no: 4, bbox: [10, 20, 30, 40] } },
    searchParams: new URLSearchParams("version_id=99&page=1"),
    currentVersion: { id: 99 },
  }), { versionId: 11, page: 4, bbox: [10, 20, 30, 40] })
})

test("timeline version numbers resolve to ids without confusing the two", () => {
  assert.deepEqual(materialFocus({
    searchParams: new URLSearchParams({ version_no: "2", page: "3", bbox: "[1,2,3,4]" }),
    versions: [{ id: 17, version_no: 1 }, { id: 42, version_no: 2 }], currentVersion: { id: 51 },
  }), { versionId: 42, page: 3, bbox: [1, 2, 3, 4] })
})

test("invalid link coordinates and page values safely fall back", () => {
  assert.deepEqual(materialFocus({ searchParams: new URLSearchParams("page=-1&bbox=bad"), currentVersion: { id: 3 } }), { versionId: 3, page: 1, bbox: null })
  for (const value of ["", "3.2", "0", "-1", Infinity]) assert.equal(positiveInteger(value), null)
  for (const value of [null, {}, [1, 2, 3], [3, 2, 1, 4], [0, 0, Infinity, 2]]) assert.equal(validBbox(value), null)
})

test("matched ZIP entries also need import confirmation; imported and skipped entries are never resubmitted", () => {
  const items = [
    { item_id: 1, status: "MATCHED", matched_archive: { id: 5 } },
    { item_id: 2, status: "UNMATCHED" },
    { item_id: 3, status: "IMPORTED", matched_archive: { id: 6 } },
    { item_id: 4, status: "SKIPPED", matched_archive: { id: 7 } },
    { item_id: 5, status: "FAILED" },
  ]
  assert.deepEqual(batchAssignmentBody(items, { 2: { archive_id: "12", material_type_id: "4" }, 5: { skip: true } }), {
    assignments: [{ item_id: 1, archive_id: 5 }, { item_id: 2, archive_id: 12, material_type_id: 4 }], skip_item_ids: [5],
  })
  assert.deepEqual(batchAssignmentBody([{ item_id: 1, status: "MATCHED", matched_archive: { id: 5 } }], { 1: { archive_id: "" } }), { assignments: [], skip_item_ids: [] })
})

test("partial assignment responses preserve untouched rows and permit retrying only failures", () => {
  const original = [{ item_id: 1, status: "MATCHED", matched_archive: { id: 5 } }, { item_id: 2, status: "UNMATCHED" }, { item_id: 3, status: "UNMATCHED" }]
  const merged = mergeBatchItems(original, { items: [{ item_id: 1, status: "IMPORTED", matched_archive: { id: 5 }, error: "上一次失败" }, { item_id: 2, status: "FAILED", error: "提交包审核中" }] }, [3])
  assert.equal(merged[0].status, "IMPORTED")
  assert.equal(merged[0].error, null)
  assert.equal(merged[1].error, "提交包审核中")
  assert.equal(merged[2].status, "SKIPPED")
  assert.deepEqual(batchAssignmentBody(merged, { 2: { archive_id: "7" } }), { assignments: [{ item_id: 2, archive_id: 7 }], skip_item_ids: [] })
  assert.equal(original[0].status, "MATCHED")
})
