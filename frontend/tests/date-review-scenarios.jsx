import React, { act } from 'react'
import { createRoot } from 'react-dom/client'
import assert from 'node:assert/strict'
import { api } from '../src/api/client'
import ParsedTextPanel from '../src/components/material/ParsedTextPanel'

const wait = () => new Promise(resolve => setTimeout(resolve, 20))
const sample = () => ({material_id: 5, version_id: 9, parser: 'OCR', full_text: '申请日期2026年9月15日',
  extracted_fields: {}, pages: [], warnings: [], page_count: 1,
  extractions: [{id: 13, node_code: 'T02', seq_index: 0, date: '2026-09-15', end_date: null,
    hours: null, raw_text: '2026年9月15日', page_no: 1, method: 'RULE', confidence: .2,
    usable: false, review_reason: 'OCR 日期识别置信度不足，须对照原图确认'}]})
async function click(node) { assert.ok(node); await act(async () => { node.click(); await wait() }) }
const save = () => [...document.querySelectorAll('button')].find(node => node.textContent === '保存校正')
async function panel(run, {editable = true, fail = false} = {}) {
  const adapter = api.defaults.adapter
  const saved = []
  api.defaults.adapter = async config => ({config, status: 200, headers: {}, data: {code: 0,
    data: {time_nodes: [{code: 'T02', name: '申请日期', value_kind: 'DATE', is_active: true}]}}})
  const root = createRoot(document.getElementById('root'))
  try {
    await act(async () => { root.render(<ParsedTextPanel parsed={sample()} editable={editable} onSave={async body => {
      saved.push(body); if (fail) throw new Error('确认保存失败')
    }} />); await wait() })
    await act(async () => { await wait() })
    await run(saved)
  } finally { await act(async () => root.unmount()); api.defaults.adapter = adapter }
}
async function reason(value) {
  await act(async () => {
    const node = document.querySelector('textarea[aria-label="时间节点校正原因"]')
    assert.ok(node)
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(node, value)
    node.dispatchEvent(new Event('input', {bubbles: true})); await wait()
  })
}

export async function runDateReviewScenarios() {
  const results = []
  const test = async (name, fn) => {
    try { await fn(); results.push({name, passed: true}) }
    catch (error) { results.push({name, passed: false, error: error.stack || error.message}) }
  }
  await test('低置信日期明确提示待确认，直接保存正文不会默认确认日期', () => panel(async saved => {
    assert.match(document.body.textContent, /OCR 日期识别置信度不足/)
    await click(save())
    assert.equal(saved[0].extractions, undefined)
  }))
  await test('日期不改值也可显式确认，必须填写原图核对依据', () => panel(async saved => {
    await click(document.querySelector('input[type="checkbox"]'))
    await click(save())
    assert.equal(saved.length, 0)
    assert.match(document.body.textContent, /请填写时间节点校正原因/)
    await reason('已对照原图确认')
    await click(save())
    assert.equal(saved[0].extractions[0].extraction_id, 13)
    assert.equal(saved[0].extractions[0].date, '2026-09-15')
    assert.equal(saved[0].reason, '已对照原图确认')
  }))
  await test('日期确认保存失败保留勾选和原因，便于重试', () => panel(async saved => {
    await click(document.querySelector('input[type="checkbox"]'))
    await reason('核对依据')
    await click(save())
    assert.equal(saved.length, 1)
    assert.match(document.body.textContent, /确认保存失败/)
    assert.equal(document.querySelector('input[type="checkbox"]').checked, true)
    assert.equal(document.querySelector('textarea[aria-label="时间节点校正原因"]').value, '核对依据')
  }, {fail: true}))
  await test('只读材料显示不确定日期提醒但不能确认', () => panel(async () => {
    assert.equal(document.querySelector('input[type="checkbox"]'), null)
    assert.match(document.body.textContent, /待人工确认，未用于计算/)
  }, {editable: false}))
  return results
}
