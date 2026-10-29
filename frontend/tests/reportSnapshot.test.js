import test from 'node:test'
import assert from 'node:assert/strict'
import { reportMaterials, reportTimeline } from '../src/utils/reportSnapshot.js'

test('报告材料保留已删除材料与原始版本，不回退到当前版本', () => {
  const materials = reportMaterials({ material_versions: [{ material_id: 1, version_id: 10, version_no: 1 }, { material_id: 2, version_id: 20 }] }, [{ id: 1, current_version_id: 99, title: '材料' }])
  assert.equal(materials[0].current_version_id, 10)
  assert.equal(materials[1].current_version_id, 20)
  assert.deepEqual(reportMaterials(null, [{ id: 1, current_version_id: 99 }]), [])
})

test('历史时间轴保留区间序列来源和派生日期，旧快照不使用实时数据', () => {
  const report = { timeline_snapshot: { node_inputs: { T10: { value_kind: 'DATE_RANGE', date: '2020-01-01', end_date: '2020-01-05', hours: 24, sources: [{ material_id: 1, version_id: 10 }] }, T06: { value_kind: 'DATE_SEQ', seq: ['2020-01-01'] } }, derived: { D01: '2021-01-01' } } }
  const timeline = reportTimeline(report)
  assert.equal(timeline.nodes[0].effective.end_date, '2020-01-05')
  assert.equal(timeline.nodes[0].sources[0].version_id, 10)
  assert.equal(timeline.nodes[1].items[0].date, '2020-01-01')
  assert.equal(timeline.derived[0].date, '2021-01-01')
  assert.equal(reportTimeline({ timeline_snapshot: { nodes: { T02: '2019-01-01' } } }).nodes[0].effective.date, '2019-01-01')
})
