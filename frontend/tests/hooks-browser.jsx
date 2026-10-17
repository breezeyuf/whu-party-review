import React, { act } from "react"
import { createRoot } from "react-dom/client"
import { useRequest } from "../src/hooks/useRequest"

globalThis.IS_REACT_ACT_ENVIRONMENT = true
const root = createRoot(document.getElementById("root"))
let hook
function Harness({ fn, id, immediate = false }) {
  hook = useRequest(fn, [id], { immediate })
  return <span>{hook.loading ? "loading" : JSON.stringify(hook.data)}</span>
}
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b }); return { promise, resolve, reject } }
const assert = (value, message) => { if (!value) throw new Error(message) }
const render = (props) => act(async () => root.render(<Harness {...props} />))
const results = []
async function test(name, fn) {
  try { await fn(); results.push({ name, passed: true }) }
  catch (error) { results.push({ name, passed: false, error: error.message }) }
}

await test("reload 并发时保留最后一次请求结果", async () => {
  const old = deferred(), latest = deferred()
  let n = 0, first, second
  await render({ id: 1, fn: () => (++n === 1 ? old.promise : latest.promise) })
  await act(async () => { first = hook.run(); second = hook.run() })
  await act(async () => { latest.resolve("new"); await second })
  await act(async () => { old.resolve("old"); await first })
  assert(hook.data === "new" && !hook.loading && !hook.error, "较早请求覆盖了新结果")
})

await test("切换提交包后忽略旧请求错误", async () => {
  const old = deferred(), latest = deferred()
  await render({ id: 2, immediate: true, fn: () => old.promise })
  await render({ id: 3, immediate: true, fn: () => latest.promise })
  await act(async () => { latest.resolve("submission-3"); await latest.promise })
  await act(async () => { old.reject(new Error("obsolete")); await Promise.resolve() })
  assert(hook.data === "submission-3" && hook.error === null, "旧请求影响了新页面")
})

await test("同步异常成为页面错误状态", async () => {
  await render({ id: 4, immediate: true, fn: () => { throw new Error("sync-error") } })
  assert(hook.error?.message === "sync-error" && !hook.loading, "同步异常未被捕获")
})

await test("immediate 从关闭变为开启后自动请求", async () => {
  let calls = 0
  const fn = () => { calls += 1; return "enabled" }
  await render({ id: 5, fn, immediate: false })
  assert(calls === 0 && !hook.loading, "关闭时不应请求")
  await render({ id: 5, fn, immediate: true })
  assert(calls === 1 && hook.data === "enabled", "开启后没有请求")
})

await act(async () => root.unmount())
globalThis.__hookResults = results
document.getElementById("results").textContent = JSON.stringify(results, null, 2)
