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
  tokenStore.setTokens("old", "refresh")
})

test("concurrent expired requests share one refresh and replay with the new token", async () => {
  let refreshCount = 0
  api.defaults.adapter = async (config) => {
    if (config.url === "/auth/refresh") {
      refreshCount += 1
      await delay(10)
      return success(config, { access_token: "new", refresh_token: "new-refresh" })
    }
    if (config.headers.Authorization === "Bearer old") return failure(config, 401)
    return success(config, config.url)
  }
  assert.deepEqual(await Promise.all([api.get("/one"), api.get("/two")]), ["/one", "/two"])
  assert.equal(refreshCount, 1)
  assert.equal(tokenStore.access, "new")
})

test("a business failure after a successful refresh keeps the valid session", async () => {
  api.defaults.adapter = async (config) => {
    if (config.url === "/auth/refresh") return success(config, { access_token: "new", refresh_token: "new-refresh" })
    return failure(config, config._retry ? 500 : 401)
  }
  await assert.rejects(api.get("/server-failure"), { status: 500 })
  assert.equal(tokenStore.access, "new")
  assert.equal(redirects.length, 0)
})

test("late responses from the old token reuse the refreshed session", async () => {
  let refreshCount = 0
  api.defaults.adapter = async (config) => {
    if (config.url === "/auth/refresh") {
      refreshCount += 1
      return success(config, { access_token: "new", refresh_token: "new-refresh" })
    }
    if (config.headers.Authorization === "Bearer old") {
      await delay(config.url === "/late" ? 30 : 0)
      return failure(config, 401)
    }
    return success(config, config.url)
  }
  assert.deepEqual(await Promise.all([api.get("/early"), api.get("/late")]), ["/early", "/late"])
  assert.equal(refreshCount, 1)
})

test("a failed refresh releases all waiting requests", async () => {
  let refreshCount = 0
  api.defaults.adapter = async (config) => {
    if (config.url === "/auth/refresh") { refreshCount += 1; await delay(10) }
    return failure(config, 401)
  }
  const result = await Promise.allSettled([api.get("/one"), api.get("/two")])
  assert.ok(result.every((item) => item.status === "rejected"))
  assert.equal(refreshCount, 1)
  assert.equal(tokenStore.access, "")
  assert.deepEqual(redirects, ["/login"])
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
