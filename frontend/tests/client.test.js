import assert from "node:assert/strict"
import { beforeEach, test } from "node:test"
import { AxiosError } from "axios"
import { api, tokenStore } from "../src/api/client.js"

const storage = new Map()
const redirects = []
globalThis.localStorage = {
  getItem: (key) => storage.get(key) ?? null,
  setItem: (key, value) => storage.set(key, value),
  removeItem: (key) => storage.delete(key),
}
globalThis.location = { pathname: "/review/tasks", assign: (url) => redirects.push(url) }
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const success = (config, data) => ({ config, status: 200, headers: {}, data: { code: 0, data } })
function failure(config, status, message = "失败") {
  throw new AxiosError(message, "ERR_BAD_RESPONSE", config, null, {
    config, status, headers: {}, data: { code: status * 100, message },
  })
}

beforeEach(() => {
  storage.clear()
  redirects.length = 0
  tokenStore.setRole("STUDENT@2")
})

test("cookie requests send no readable credentials and clear legacy tokens", async () => {
  storage.set("prw_access", "legacy-access")
  storage.set("prw_refresh", "legacy-refresh")
  api.defaults.adapter = async (config) => {
    assert.equal(config.withCredentials, true)
    assert.equal(config.headers.Authorization, undefined)
    assert.equal(config.headers["X-Requested-With"], "party-review")
    assert.equal(config.headers["X-Active-Role"], "STUDENT@2")
    return success(config, { ok: true })
  }
  assert.deepEqual(await api.post("/materials", {}), { ok: true })
  assert.equal(storage.has("prw_access"), false)
  assert.equal(storage.has("prw_refresh"), false)
})

test("expired cookie requests redirect once without refresh or replay", async () => {
  const urls = []
  api.defaults.adapter = async (config) => { urls.push(config.url); return failure(config, 401) }
  const results = await Promise.allSettled([api.get("/one"), api.get("/two")])
  assert.ok(results.every((item) => item.status === "rejected"))
  assert.deepEqual(urls, ["/one", "/two"])
  assert.deepEqual(redirects, ["/login"])
  assert.equal(tokenStore.role, "")
})

test("anonymous session bootstrap does not force navigation", async () => {
  api.defaults.adapter = async (config) => failure(config, 401)
  await assert.rejects(api.get("/auth/me"), { status: 401 })
  assert.equal(redirects.length, 0)
})

test("invalid login does not trigger refresh", async () => {
  const urls = []
  api.defaults.adapter = async (config) => { urls.push(config.url); return failure(config, 401) }
  await assert.rejects(api.post("/auth/login", {}), { status: 401 })
  assert.deepEqual(urls, ["/auth/login"])
})

test("blob download errors retain the server message", async () => {
  api.defaults.adapter = async (config) => {
    throw new AxiosError("download failed", "ERR_BAD_RESPONSE", config, null, {
      status: 403, data: new Blob([JSON.stringify({ code: 40300, message: "无权下载材料" })]),
    })
  }
  await assert.rejects(api.get("/materials/1/file", { responseType: "blob" }), { message: "无权下载材料", code: 40300 })
})
