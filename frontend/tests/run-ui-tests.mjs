import { JSDOM } from "jsdom"
import { createServer } from "vite"
import { fileURLToPath } from "node:url"

const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: "http://localhost/" })
for (const name of ["window", "document", "HTMLElement", "HTMLInputElement", "HTMLTextAreaElement", "HTMLSelectElement", "Event", "MouseEvent", "KeyboardEvent", "File", "FormData", "localStorage"]) {
  globalThis[name] = name === "window" ? dom.window : dom.window[name]
}
Object.defineProperty(globalThis, "navigator", { value: dom.window.navigator, configurable: true })
globalThis.IS_REACT_ACT_ENVIRONMENT = true
globalThis.requestAnimationFrame = (fn) => setTimeout(fn, 0)
globalThis.cancelAnimationFrame = clearTimeout
URL.createObjectURL = () => "blob:ui-test"
URL.revokeObjectURL = () => {}

const server = await createServer({ root: fileURLToPath(new URL("..", import.meta.url)), server: { middlewareMode: true }, appType: "custom", logLevel: "error" })
try {
  const { runUiScenarios } = await server.ssrLoadModule("/tests/ui-scenarios.jsx")
  const results = await runUiScenarios()
  const { runIdentityScenarios } = await server.ssrLoadModule("/tests/identity-scenarios.jsx")
  results.push(...await runIdentityScenarios())
  const { runStatsFilterScenarios } = await server.ssrLoadModule("/tests/stats-filter-scenarios.jsx")
  results.push(...await runStatsFilterScenarios())
  const { runOcrReviewScenarios } = await server.ssrLoadModule("/tests/ocr-review-scenarios.jsx")
  results.push(...await runOcrReviewScenarios())
  const { runDateReviewScenarios } = await server.ssrLoadModule("/tests/date-review-scenarios.jsx")
  results.push(...await runDateReviewScenarios())
  for (const result of results) console.log(`${result.passed ? "PASS" : "FAIL"} ${result.name}${result.error ? `: ${result.error}` : ""}`)
  console.log(`UI scenarios: ${results.filter((result) => result.passed).length}/${results.length} passed (isolated API fixtures, no database writes)`)
  process.exitCode = results.some((result) => !result.passed) ? 1 : 0
} finally {
  await server.close()
  dom.window.close()
}
