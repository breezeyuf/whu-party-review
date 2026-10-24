import test from "node:test"
import assert from "node:assert/strict"
import { pagePoint, regionBox } from "../src/utils/regionSelection.js"
import { extractionChanges, extractionDraft } from "../src/utils/extractionWorkflow.js"

const defs = [{ code: "T02", value_kind: "DATE", is_active: true }, { code: "T06", value_kind: "DATE_SEQ", is_active: true }, { code: "T10", value_kind: "DATE_RANGE", has_hours: true, is_active: true }, { code: "D01", value_kind: "DERIVED", is_active: true }]
test("框选使用实际显示尺寸换算，反向拖动得到相同 PDF 坐标", () => {
  const rect = { left: 100, top: 40, width: 300, height: 400 }
  const a = pagePoint(130, 80, rect, 600, 800)
  const b = pagePoint(280, 240, rect, 600, 800)
  assert.deepEqual(regionBox(a, b), [60, 80, 360, 400])
  assert.deepEqual(regionBox(b, a), [60, 80, 360, 400])
  assert.deepEqual(pagePoint(160, 120, { ...rect, width: 600, height: 800 }, 600, 800), a)
})
test("移出页面的拖动被限制到页内，无尺寸时不生成坐标", () => {
  assert.deepEqual(pagePoint(-10, 900, { left: 0, top: 0, width: 300, height: 400 }, 600, 800), [0, 800])
  assert.equal(pagePoint(0, 0, { width: 0, height: 0 }, 600, 800), null)
})
test("只提交变更节点，保留未改动自动抽取记录", () => {
  const original = [{ id: 1, node_code: "T02", date: "2026-01-01", seq_index: 0 }, { id: 2, node_code: "T06", date: "2026-02-01", seq_index: 1 }]
  const drafts = original.map((ex) => extractionDraft(ex))
  drafts[1].date = "2026-02-02"
  assert.deepEqual(extractionChanges(original, drafts, defs), [{ extraction_id: 2, node_code: "T06", date: "2026-02-02", end_date: null, hours: null, seq_index: 1 }])
  assert.equal(original[1].date, "2026-02-01")
})
test("新增区间与学时、删除记录形成明确增量", () => {
  const old = { id: 1, node_code: "T02", date: "2026-01-01" }
  const drafts = [{ ...extractionDraft(old), deleted: true }, { ...extractionDraft({}, "new-1"), node_code: "T10", date: "2026-03-01", end_date: "2026-03-03", hours: "24" }]
  const changes = extractionChanges([old], drafts, defs)
  assert.deepEqual(changes[0], { extraction_id: 1, delete: true })
  assert.equal(changes[1].hours, 24)
  assert.equal(changes[1].end_date, "2026-03-03")
})
test("不合法日期、倒序区间、负学时、派生节点与非法序号阻止提交", () => {
  const base = { ...extractionDraft({}, "new"), node_code: "T10", date: "2026-03-01" }
  for (const patch of [{ date: "2026-02-30" }, { end_date: "2026-02-28" }, { hours: -1 }, { hours: "Infinity" }, { node_code: "D01" }, { seq_index: 1.5 }]) {
    assert.throws(() => extractionChanges([], [{ ...base, ...patch }], defs))
  }
})
test("未修改的原始无效记录不妨碍文本校正，撤销删除不发节点操作", () => {
  const old = { id: 1, node_code: "T02", date: null, invalid_reason: "原文日期不完整" }
  assert.deepEqual(extractionChanges([old], [extractionDraft(old)], defs), [])
})
