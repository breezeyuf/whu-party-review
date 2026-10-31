import React, { act } from "react"
import assert from "node:assert/strict"
import { createRoot } from "react-dom/client"
import { createMemoryRouter, RouterProvider } from "react-router-dom"
import { AuthProvider, useAuth } from "../src/context/AuthContext"
import { ToastProvider } from "../src/context/ToastContext"
import { api, tokenStore } from "../src/api/client"
import { appRoutes } from "../src/routes"
import { FALLBACK_META } from "../src/utils/constants"
import { roleKey } from "../src/utils/identity"

const pause = (ms = 30) => new Promise((resolve) => setTimeout(resolve, ms))
const flush = () => act(async () => { await pause(); await pause() })
let root, router, auth, requests
const text = () => document.getElementById("root").textContent
const button = (label) => [...document.querySelectorAll("button")].find((node) => node.textContent.trim() === label)
function Probe({ children }) { auth = useAuth(); return children }
async function navigate(path) { await act(async () => { await router.navigate(path) }); await flush() }
async function click(node) { assert.ok(node, "按钮不存在"); await act(async () => { node.click(); await pause() }); await flush() }
async function fill(node, value) {
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(node, value)
    node.dispatchEvent(new Event("input", { bubbles: true }))
    await pause()
  })
}
async function cleanup() {
  if (root) { await act(async () => root.unmount()); root = null }
  router?.dispose()
  tokenStore.clear()
}
async function mount({ roles = [{ role: "STUDENT", org_id: 2 }], path = "/login", session = false, selected = "", passwordChange = false, failMe, failLogin = false, authMode = "demo", failLogout = false } = {}) {
  await cleanup()
  requests = []
  let authenticated = session
  tokenStore.setRole(selected)
  api.defaults.adapter = async (config) => {
    requests.push({ url: config.url, method: config.method, role: config.headers["X-Active-Role"] })
    let data
    if (config.url === "/auth/login") {
      if (failLogin) throw new Error("账号或密码错误")
      authenticated = true
      data = { user: { roles }, must_change_password: passwordChange }
    } else if (config.url === "/auth/config") data = { mode: authMode }
    else if (config.url === "/auth/me") {
      if (!authenticated) throw new Error("未登录")
      if (failMe?.(config)) throw new Error("身份验证服务暂不可用")
      const active = roles.find((role) => roleKey(role) === config.headers["X-Active-Role"]) || roles[0]
      data = { auth_mode: authMode, id: 77, username: "test", real_name: "身份测试用户", org_name: "测试组织", roles, active_role: active, must_change_password: passwordChange }
    } else if (config.url === "/auth/logout") {
      if (failLogout) throw new Error("退出服务暂不可用")
      authenticated = false; data = {}
    } else if (config.url === "/auth/demo-accounts") data = []
    else if (config.url === "/meta") data = FALLBACK_META
    else if (config.url === "/messages/unread-count") data = { count: 0 }
    else if (config.url === "/dashboard") data = { role: auth.activeRole.role, archive_id: null, todo: { to_review: 3 } }
    else throw new Error(`不应加载此接口：${config.url}`)
    return { config, status: 200, statusText: "OK", headers: {}, data: { code: 0, message: "ok", data } }
  }
  document.getElementById("root").innerHTML = ""
  router = createMemoryRouter(appRoutes, { initialEntries: [path] })
  root = createRoot(document.getElementById("root"))
  await act(async () => root.render(<ToastProvider><AuthProvider><Probe><RouterProvider router={router} /></Probe></AuthProvider></ToastProvider>))
  // Wait for lazy route imports as well as the auth request.
  await act(async () => { await pause(350) })
  await flush()
}
async function login() {
  await fill(document.querySelector('[autocomplete="username"]'), "test")
  await fill(document.querySelector('[type="password"]'), "Test123!")
  await act(async () => { document.querySelector("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })); await pause(100) })
  await flush()
}
const nav = () => document.querySelector('nav[aria-label="主要导航"]')?.textContent || ""

export async function runIdentityScenarios() {
  const results = []
  const test = async (name, fn) => {
    try { await fn(); results.push({ name, passed: true }) }
    catch (error) { results.push({ name, passed: false, error: error.stack || error.message }) }
  }
  await test("未登录访问管理地址先进入登录页，不加载管理或仪表盘接口", async () => {
    await mount({ path: "/admin/users" })
    assert.equal(router.state.location.pathname, "/login")
    assert.ok(!requests.some((r) => ["/users", "/dashboard", "/meta"].includes(r.url)))
  })
  await test("学生登录自动进入学生端，无管理、审核菜单或身份切换器", async () => {
    await mount(); await login()
    assert.equal(router.state.location.pathname, "/student")
    assert.match(text(), /申请学生工作台/)
    assert.match(nav(), /我的材料/)
    assert.doesNotMatch(nav(), /管理|审核待办|规则库/)
    assert.equal(document.querySelector('[aria-label="切换当前角色"]'), null)
  })
  await test("管理员登录直接进入管理端，管理功能默认可见", async () => {
    await mount({ roles: [{ role: "SYS_ADMIN", org_id: 1 }] }); await login()
    assert.equal(router.state.location.pathname, "/admin")
    assert.match(text(), /系统管理员工作台/)
    assert.match(nav(), /组织与系统管理.*用户管理.*系统配置/)
    assert.doesNotMatch(nav(), /我的材料|整改中心|审核待办/)
    assert.equal(document.querySelector('a[href="/admin/users"]')?.closest("ul")?.hidden, false)
  })
  await test("审核员登录直接进入审核端，不显示学生或系统管理入口", async () => {
    await mount({ roles: [{ role: "BRANCH_REVIEWER", org_id: 2 }] }); await login()
    assert.equal(router.state.location.pathname, "/review")
    assert.match(text(), /审核员工作台/)
    assert.match(nav(), /审核待办/)
    assert.doesNotMatch(nav(), /我的材料|用户管理|系统配置/)
  })
  await test("学生手动访问管理员和审核业务地址被拦截，业务接口不发出", async () => {
    await mount({ session: true })
    for (const path of ["/admin/users", "/admin/settings", "/review/tasks", "/archives", "/rules/checklists"]) {
      await navigate(path)
      assert.equal(router.state.location.pathname, "/403")
    }
    assert.ok(!requests.some((r) => ["/users", "/settings", "/submissions", "/archives", "/rules/checklists"].includes(r.url)))
  })
  await test("管理员与审核员不能访问学生页面，学生业务接口不发出", async () => {
    for (const role of ["SYS_ADMIN", "ORG_ADMIN", "BRANCH_REVIEWER"]) {
      await mount({ roles: [{ role, org_id: 1 }], session: true })
      for (const path of ["/my/materials", "/my/progress", "/my/rectification", "/my/self-check/101"]) {
        await navigate(path); assert.equal(router.state.location.pathname, "/403")
      }
      assert.ok(!requests.some((r) => r.url === "/my/archive" || r.url.startsWith("/submissions/101")))
    }
  })
  await test("访问其他身份首页回到自己的首页，刷新登录态仍保持当前身份", async () => {
    await mount({ session: true, selected: "STUDENT@2", path: "/admin" })
    assert.equal(router.state.location.pathname, "/student")
    await navigate("/review"); assert.equal(router.state.location.pathname, "/student")
    assert.ok(requests.filter((r) => r.url === "/dashboard").every((r) => r.role === "STUDENT@2"))
  })
  const multiple = [{ role: "STUDENT", org_id: 2 }, { role: "BRANCH_REVIEWER", org_id: 3 }]
  await test("多身份账号先选择已授权身份，选择前不加载任何工作台", async () => {
    await mount({ roles: multiple }); await login()
    assert.equal(router.state.location.pathname, "/choose-identity")
    assert.equal(document.querySelectorAll(".identity-choice").length, 2)
    assert.doesNotMatch(text(), /系统管理员/)
    assert.ok(!requests.some((r) => r.url === "/dashboard"))
    await click(document.querySelectorAll(".identity-choice")[1])
    assert.equal(router.state.location.pathname, "/review")
    assert.equal(tokenStore.role, "BRANCH_REVIEWER@3")
    assert.doesNotMatch(nav(), /我的材料/)
    assert.equal(document.querySelector('[aria-label="切换当前角色"]'), null)
  })
  await test("未选择身份时刷新或直接输入业务地址仍回选择页", async () => {
    await mount({ roles: multiple, session: true, path: "/my/materials" })
    assert.equal(router.state.location.pathname, "/choose-identity")
    assert.equal(tokenStore.role, "")
    assert.ok(!requests.some((r) => ["/dashboard", "/my/archive"].includes(r.url)))
  })
  await test("个人中心只显示当前办理身份与组织", async () => {
    const roles = [{ role: "STUDENT", org_id: 2, org_name: "学生组织" }, { role: "BRANCH_REVIEWER", org_id: 3, org_name: "审核组织" }]
    await mount({ roles, session: true, selected: "STUDENT@2", path: "/profile" })
    assert.match(text(), /当前身份发展学生/)
    assert.match(text(), /当前组织学生组织/)
    assert.doesNotMatch(text(), /党支部审核员|审核组织/)
  })
  await test("多身份会话恢复已选身份，携带精确的组织范围", async () => {
    await mount({ roles: multiple, session: true, selected: "BRANCH_REVIEWER@3", path: "/" })
    assert.equal(router.state.location.pathname, "/review")
    assert.ok(requests.filter((r) => r.url === "/dashboard").every((r) => r.role === "BRANCH_REVIEWER@3"))
  })
  await test("身份验证失败保留选择页并恢复原请求身份，允许重试", async () => {
    let fail = true
    await mount({ roles: multiple, session: true, failMe: (config) => fail && config.headers["X-Active-Role"] === "BRANCH_REVIEWER@3" })
    await click(document.querySelectorAll(".identity-choice")[1])
    assert.equal(router.state.location.pathname, "/choose-identity")
    assert.equal(tokenStore.role, "")
    assert.match(text(), /身份验证服务暂不可用/)
    fail = false
    await click(document.querySelectorAll(".identity-choice")[1])
    assert.equal(router.state.location.pathname, "/review")
  })
  await test("伪造未授权身份在请求发出前被拒绝", async () => {
    await mount({ session: true })
    const count = requests.length
    await act(async () => { await assert.rejects(auth.switchRole({ role: "SYS_ADMIN", org_id: 1 }), /没有此身份/) })
    assert.equal(requests.length, count)
    assert.equal(tokenStore.role, "STUDENT@2")
  })
  await test("重新登录清除上一个账号的角色头，按新账号的真实身份进入", async () => {
    await mount({ selected: "SYS_ADMIN@1" }); await login()
    assert.equal(router.state.location.pathname, "/student")
    assert.equal(requests.filter((r) => r.url === "/auth/me").at(-1).role, undefined)
    assert.equal(tokenStore.role, "STUDENT@2")
  })
  await test("登录后的身份查询失败不残留令牌或半登录状态", async () => {
    await mount({ failMe: () => true }); await login()
    assert.equal(router.state.location.pathname, "/login")
    assert.equal(tokenStore.role, "")
    assert.equal(tokenStore.role, "")
    assert.equal(auth.user, null)
    assert.match(text(), /身份验证服务暂不可用/)
  })
  await test("错误密码不进入工作台，首次改密优先于多身份选择", async () => {
    await mount({ failLogin: true }); await login()
    assert.equal(router.state.location.pathname, "/login")
    assert.match(text(), /账号或密码错误/)
    await mount({ roles: multiple, passwordChange: true }); await login()
    assert.equal(router.state.location.pathname, "/change-password")
    assert.ok(!requests.some((r) => r.url === "/dashboard"))
  })
  await test("退出后重新登录另一身份，不残留前一个身份的页面和菜单", async () => {
    await mount({ roles: [{ role: "SYS_ADMIN", org_id: 1 }], session: true })
    assert.match(nav(), /组织与系统管理/)
    await click(button("退出登录"))
    assert.equal(router.state.location.pathname, "/login")
    assert.equal(document.querySelector('nav[aria-label="主要导航"]'), null)
    assert.equal(tokenStore.role, "")
    await mount(); await login()
    assert.doesNotMatch(nav(), /用户管理|系统配置/)
    assert.equal(router.state.location.pathname, "/student")
  })
  await test("统一认证登录页仅显示学校入口，不显示本地密码或演示账号", async () => {
    await mount({ authMode: "sso" })
    assert.equal(document.querySelector('input[type="password"]'), null)
    assert.equal(document.querySelector('a[href="/api/auth/sso/start"]')?.textContent, "学校统一身份认证")
    assert.ok(!requests.some((r) => r.url === "/auth/demo-accounts"))
  })
  await test("统一认证个人中心隐藏本地改密入口", async () => {
    await mount({ authMode: "sso", session: true, path: "/profile" })
    assert.equal(router.state.location.pathname, "/profile")
    assert.equal(document.querySelector('input[type="password"]'), null)
  })
  await test("退出失败保留当前界面并提示重试", async () => {
    await mount({ session: true, failLogout: true })
    await click(button("退出登录"))
    assert.ok(auth.user)
    assert.notEqual(router.state.location.pathname, "/login")
    assert.match(text(), /退出服务暂不可用/)
  })
  await cleanup()
  return results
}
