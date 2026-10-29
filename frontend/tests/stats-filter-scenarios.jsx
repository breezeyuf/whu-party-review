import React, { act, useState } from "react"
import { createRoot } from "react-dom/client"
import assert from "node:assert/strict"
import { api, tokenStore } from "../src/api/client"
import { AuthProvider } from "../src/context/AuthContext"
import StatsFilters from "../src/components/charts/StatsFilters"

const organizations = [
  { id: 1, org_type: "SCHOOL", name: "学校" },
  { id: 10, org_type: "COLLEGE", parent_id: 1, name: "第一学院" },
  { id: 11, org_type: "BRANCH", parent_id: 10, name: "第一支部" },
  { id: 12, org_type: "BRANCH", parent_id: 10, name: "第二支部" },
  { id: 20, org_type: "COLLEGE", parent_id: 1, name: "另一学院" },
  { id: 21, org_type: "BRANCH", parent_id: 20, name: "另一学院支部" },
]
const wait = () => new Promise((resolve) => setTimeout(resolve, 15))
const field = (name) => [...document.querySelectorAll("label")].find((label) => label.querySelector("span")?.textContent === name)?.querySelector("select")
const choices = (name) => [...field(name).options].map((option) => option.value).filter(Boolean)
const selected = () => JSON.parse(document.querySelector("output").textContent)
async function choose(name, value) {
  await act(async () => {
    const select = field(name)
    Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set.call(select, value)
    select.dispatchEvent(new Event("change", { bubbles: true }))
    await wait()
  })
}

function Harness() {
  const [value, setValue] = useState({})
  return <><StatsFilters value={value} onChange={setValue} /><output>{JSON.stringify(value)}</output></>
}

async function withRole(role, run) {
  const adapter = api.defaults.adapter
  const requests = []
  const container = document.getElementById("root")
  container.innerHTML = ""
  const root = createRoot(container)
  tokenStore.setTokens("stats-test-token", "stats-test-refresh")
  tokenStore.setRole(`${role.role}@${role.org_id}`)
  api.defaults.adapter = async (config) => {
    requests.push(config)
    const data = config.url === "/auth/me" ? { id: 1, active_role: role, roles: [role] }
      : config.url === "/orgs" ? organizations
      : config.url === "/batches" ? { items: [], total: 0 }
      : assert.fail(`Unexpected stats filter request: ${config.url}`)
    return { config, status: 200, statusText: "OK", headers: {}, data: { code: 0, data } }
  }
  try {
    await act(async () => { root.render(<AuthProvider><Harness /></AuthProvider>); await wait() })
    await act(async () => { await wait() })
    await run(requests)
  } finally {
    await act(async () => root.unmount())
    api.defaults.adapter = adapter
    tokenStore.clear()
  }
}

export async function runStatsFilterScenarios() {
  const results = []
  const test = async (name, run) => {
    try { await run(); results.push({ name, passed: true }) }
    catch (error) { results.push({ name, passed: false, error: error.stack || error.message }) }
  }
  for (const role of ["SYS_ADMIN", "ORG_ADMIN"]) {
    await test(`${role} 统计可选后端返回的学院和支部，切换学院清除旧支部`, () => withRole({ role, org_id: 1 }, async (requests) => {
      assert.deepEqual(choices("学院"), ["10", "20"])
      assert.deepEqual(choices("支部"), ["11", "12", "21"])
      await choose("学院", "20")
      assert.deepEqual(choices("支部"), ["21"])
      await choose("支部", "21")
      assert.equal(selected().branch_id, "21")
      await choose("学院", "10")
      assert.equal(selected().branch_id, "")
      assert.deepEqual(choices("支部"), ["11", "12"])
      assert.ok(requests.some((request) => request.url === "/orgs" && request.params.flat === true))
      assert.ok(requests.every((request) => ["/auth/me", "/orgs", "/batches"].includes(request.url)))
    }))
  }
  await test("学院审核员统计筛选仍只列本学院及其支部", () => withRole({ role: "COLLEGE_REVIEWER", org_id: 10 }, async () => {
    assert.deepEqual(choices("学院"), ["10"])
    assert.deepEqual(choices("支部"), ["11", "12"])
  }))
  await test("支部审核员统计筛选不增加其他支部", () => withRole({ role: "BRANCH_REVIEWER", org_id: 11 }, async () => {
    assert.deepEqual(choices("学院"), [])
    assert.deepEqual(choices("支部"), ["11"])
  }))
  return results
}
