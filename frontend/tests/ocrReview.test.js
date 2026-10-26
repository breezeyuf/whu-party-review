import test from "node:test"
import assert from "node:assert/strict"
import { applyOcrSuggestion } from "../src/utils/ocrReview.js"
import { settingsPatch } from "../src/utils/settingsWorkflow.js"

test("本地 OCR 只允许 RapidOCR、自动或关闭", () => {
  assert.equal(settingsPatch("ocr",{engine:"rapidocr"}).engine,"rapidocr")
  assert.equal(settingsPatch("ocr",{engine:"none"}).engine,"none")
  assert.throws(() => settingsPatch("ocr",{engine:"paddleocr"}))
})

test("OCR suggestion replaces only its source and retains other manual changes", () => {
  assert.equal(applyOcrSuggestion("已手动改过\n2026-1-2", {}, {}, { status: "pending", original_text: "2026-1-2", candidate_text: "2026-1-24" }), "已手动改过\n2026-1-24")
})
test("OCR suggestion refuses ambiguous or already edited text", () => {
  for (const text of ["日期 日期", "已校正"]) assert.throws(() => applyOcrSuggestion(text, {}, {}, { status: "pending", original_text: "日期", candidate_text: "日期2" }))
})
test("empty OCR page is filled in its own position", () => {
  const parsed = { full_text: "前页\n\n后页", pages: [{ page_no: 1, text: "前页" }, { page_no: 2, text: "" }, { page_no: 3, text: "后页" }] }
  assert.equal(applyOcrSuggestion(parsed.full_text, parsed, parsed.pages[1], { status: "pending", original_text: "", candidate_text: "新识别文字", block_index: null }), "前页\n新识别文字\n后页")
})
test("vision settings support fractional confidence and constrain request budget", () => {
  assert.equal(settingsPatch("ocr_vision", { confidence_threshold: "0.85" }).confidence_threshold, 0.85)
  assert.throws(() => settingsPatch("ocr_vision", { max_regions: 21 }))
  assert.throws(() => settingsPatch("ocr_vision", { timeout_s: 121 }))
})
