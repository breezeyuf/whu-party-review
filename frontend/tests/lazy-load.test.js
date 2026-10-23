import test from "node:test"
import assert from "node:assert/strict"
import { createElement, Suspense } from "react"
import { renderToString } from "react-dom/server"
import { isChunkLoadError, lazyWithRetry, loadWithRetry } from "../src/utils/lazyLoad.js"

const module = { default: () => null }
const chunkError = () => new TypeError("Failed to fetch dynamically imported module: /assets/Page-old.js")

test("a failed page download is retried once before succeeding", async () => {
  let calls = 0
  const result = await loadWithRetry(async () => { calls += 1; if (calls === 1) throw chunkError(); return module }, { delay: 0 })
  assert.equal(result, module)
  assert.equal(calls, 2)
})

test("two failed downloads reject with an error marked as a download failure", async () => {
  let calls = 0
  await assert.rejects(() => loadWithRetry(async () => { calls += 1; throw chunkError() }, { delay: 0 }), (error) => isChunkLoadError(error))
  assert.equal(calls, 2)
  assert.equal(isChunkLoadError(new Error("Cannot read properties of undefined")), false)
  assert.equal(isChunkLoadError(new Error("error loading dynamically imported module")), true)
})

test("preload and render share the same in-flight download", async () => {
  let calls = 0
  let finish
  const Page = lazyWithRetry(() => { calls += 1; return new Promise((resolve) => { finish = resolve }) }, { delay: 0 })
  const first = Page.preload()
  const second = Page.preload()
  assert.equal(first, second)
  finish(module)
  assert.equal(await first, module)
  assert.equal(await Page.preload(), module)
  assert.equal(calls, 1)
})

test("a preloaded page renders immediately without showing the loading fallback", async () => {
  let calls = 0
  const Page = lazyWithRetry(async () => { calls += 1; return { default: () => createElement("p", null, "已下载的页面") } }, { delay: 0 })
  await Page.preload()
  const html = renderToString(createElement(Suspense, { fallback: "正在加载…" }, createElement(Page)))
  assert.match(html, /已下载的页面/)
  assert.doesNotMatch(html, /正在加载/)
  assert.equal(calls, 1)
})

test("a failed preload is not cached, so a later render downloads again", async () => {
  let calls = 0
  const Page = lazyWithRetry(async () => { calls += 1; if (calls <= 2) throw chunkError(); return module }, { delay: 0 })
  await assert.rejects(() => Page.preload(), (error) => isChunkLoadError(error))
  assert.equal(calls, 2)
  assert.equal(await Page.preload(), module)
  assert.equal(calls, 3)
})
