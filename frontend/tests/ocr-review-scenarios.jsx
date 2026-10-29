import React, { act } from "react"
import { createRoot } from "react-dom/client"
import assert from "node:assert/strict"
import { api } from "../src/api/client"
import ParsedTextPanel from "../src/components/material/ParsedTextPanel"

const wait = () => new Promise((resolve) => setTimeout(resolve, 15))
const initial = () => ({
  material_id: 7, version_id: 10, parser: "NONE", ocr_engine: "rapidocr", page_count: 2,
  full_text: "已有正文", corrected_text: null, extracted_fields: {}, extractions: [],
  pages: [{ page_no: 1, source: "scan", text: "", ocr_status: "NEEDS_REVIEW" },
    { page_no: 2, source: "text", text: "已有正文" }],
  warnings: [{ code: "OCR-REVIEW", page_no: 1, message: "第 1 页未识别到文字，请核对空白、照片或手写内容" }],
})
const pendingSection = () => document.querySelector('section[aria-label="OCR 待人工复核"]')
const saveButton = () => [...document.querySelectorAll("button")].find((button) => button.textContent === "保存校正")
async function click(element) {
  assert.ok(element, "未找到操作控件")
  await act(async () => { element.click(); await wait() })
}

async function withPanel(run, { editable = true, fail = false, parsed = initial() } = {}) {
  const adapter = api.defaults.adapter
  const saved = []
  const root = createRoot(document.getElementById("root"))
  api.defaults.adapter = async (config) => {
    assert.equal(config.url, "/meta")
    return { config, status: 200, statusText: "OK", headers: {}, data: { code: 0, data: { time_nodes: [] } } }
  }
  const render = async (value) => {
    await act(async () => {
      root.render(<ParsedTextPanel parsed={value} editable={editable} onSave={async (body) => {
        saved.push(body)
        if (fail) throw new Error("保存核对失败，请重试")
      }} />)
      await wait()
    })
  }
  try {
    await render(parsed)
    await run({ saved, render, parsed })
  } finally {
    await act(async () => root.unmount())
    api.defaults.adapter = adapter
  }
}

export async function runOcrReviewScenarios() {
  const results = []
  const test = async (name, fn) => {
    try { await fn(); results.push({ name, passed: true }) }
    catch (error) { results.push({ name, passed: false, error: error.stack || error.message }) }
  }
  await test("空 OCR 页显示可读提醒，混合材料直接保存不会自动确认空页", () => withPanel(async ({ saved }) => {
    assert.match(document.body.textContent, /第 1 页未识别到文字/)
    assert.ok(pendingSection())
    assert.equal(document.querySelectorAll('input[type="checkbox"]').length, 1)
    assert.equal(document.querySelector('input[type="checkbox"]').checked, false)
    await click(saveButton())
    assert.equal(saved[0].corrected_text, "已有正文")
    assert.equal(saved[0].ocr_reviewed_pages, undefined)
    assert.ok(pendingSection())
  }))
  await test("逐页核对随保存提交当前版本，收到已核对结果后移除提醒", () => withPanel(async ({ saved, render, parsed }) => {
    await click(document.querySelector('input[type="checkbox"]'))
    assert.equal(saved.length, 0)
    assert.ok(pendingSection(), "勾选本身不能改变已保存状态")
    await click(saveButton())
    assert.equal(saved[0].version_id, 10)
    assert.deepEqual(saved[0].ocr_reviewed_pages, [1])
    await render({ ...parsed, warnings: [], pages: parsed.pages.map((page) => page.page_no === 1 ? { ...page, ocr_status: "MANUALLY_REVIEWED" } : page) })
    assert.equal(pendingSection(), null)
    assert.equal(document.querySelectorAll('input[type="checkbox"]').length, 0)
  }))
  await test("保存失败保留待复核提醒和选中页号，允许重试", () => withPanel(async ({ saved }) => {
    await click(document.querySelector('input[type="checkbox"]'))
    await click(saveButton())
    assert.match(document.querySelector('[role="alert"]').textContent, /保存核对失败/)
    assert.ok(pendingSection())
    assert.equal(document.querySelector('input[type="checkbox"]').checked, true)
    await click(saveButton())
    assert.equal(saved.length, 2)
    assert.deepEqual(saved[1].ocr_reviewed_pages, [1])
  }, { fail: true }))
  await test("历史或只读材料展示空页提醒但不提供确认入口，兼容旧解析数据", () => {
    const parsed = initial()
    delete parsed.pages[0].ocr_status
    return withPanel(async () => {
      assert.match(pendingSection().textContent, /第 1 页待审核人员核对/)
      assert.equal(document.querySelectorAll('input[type="checkbox"]').length, 0)
      assert.equal(saveButton(), undefined)
    }, { parsed, editable: false })
  })
  return results
}
