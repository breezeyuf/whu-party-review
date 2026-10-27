#!/usr/bin/env node
// 前端路由体积预算：按 Vite manifest 的静态 import 闭包统计各页面 gzip 体积（仅 JS）。
//
// 用法（在 frontend 目录下）：
//   node scripts/bundle-budget.mjs                 报告
//   node scripts/bundle-budget.mjs --check         按 frontend/bundle-budget.json 检查，超标退出码 1
//   node scripts/bundle-budget.mjs --write-budget  用当前实测值刷新预算
//
// `npm run build` 已包含 --check，CI 与本地构建都会执行；确需变大时先说明原因，再刷新预算。
import { gzipSync } from "node:zlib"
import { readFileSync, writeFileSync, existsSync } from "node:fs"
import { dirname, join, resolve, relative } from "node:path"
import { fileURLToPath } from "node:url"

const HERE = dirname(fileURLToPath(import.meta.url))
const FRONTEND = resolve(HERE, "..")
const BUDGET_PATH = join(FRONTEND, "bundle-budget.json")
const DEFAULT_DIST = join(FRONTEND, "dist")
const SHELL_CANDIDATES = [
  "components/layout/AppLayout.jsx",
  "components/layout/Shell.jsx",
  "components/layout/shellModule.js",
]
const DEFAULT_ACCEPTANCE = [
  { route: "/login", key: "src/pages/LoginPage.jsx", max_kib: 125 },
  { route: "/stats/overview", key: "src/pages/stats/StatsOverviewPage.jsx", max_kib: 150 },
]
const SLACK_KIB = 0.3

const argv = process.argv.slice(2)
const check = argv.includes("--check")
const write = argv.includes("--write-budget")
const distArg = argv.find((a) => !a.startsWith("--"))
const dist = distArg ? resolve(process.cwd(), distArg) : DEFAULT_DIST

const manifestPath = join(dist, ".vite", "manifest.json")
if (!existsSync(manifestPath)) {
  console.error(`找不到 ${manifestPath}：请先运行 vite build --manifest`)
  process.exit(2)
}
const manifest = JSON.parse(readFileSync(manifestPath, "utf8"))
const sizes = new Map()

function gzipSize(rel) {
  if (!sizes.has(rel)) {
    const file = join(dist, rel)
    sizes.set(rel, existsSync(file) ? gzipSync(readFileSync(file), { level: 9 }).length : 0)
  }
  return sizes.get(rel)
}

function closure(key) {
  const seen = new Set()
  const stack = [key]
  while (stack.length) {
    const entry = manifest[stack.pop()]
    if (!entry) continue
    for (const item of [entry.file, ...(entry.css || [])]) {
      if (item) seen.add(item)
    }
    stack.push(...(entry.imports || []))
  }
  return seen
}

function measure(key) {
  let total = 0
  for (const file of closure(key)) {
    if (file.endsWith(".js")) total += gzipSize(file)
  }
  return total / 1024
}

const pageKeys = Object.keys(manifest)
  .filter((k) => k.startsWith("src/pages/") && manifest[k].isDynamicEntry)
  .sort()
const shellKey = Object.keys(manifest).find((k) => SHELL_CANDIDATES.some((name) => k.includes(name)))

let budget = { slack_kib: SLACK_KIB, acceptance: DEFAULT_ACCEPTANCE, routes: {} }
if (existsSync(BUDGET_PATH)) {
  budget = { ...budget, ...JSON.parse(readFileSync(BUDGET_PATH, "utf8")) }
}
budget.acceptance = budget.acceptance?.length ? budget.acceptance : DEFAULT_ACCEPTANCE

console.log(`[dist] ${relative(process.cwd(), dist) || dist}`)
console.log(`[shell] 外壳条目: ${shellKey || "（非独立条目，计入入口包）"}`)
console.log(`[entry] 入口包 JS ${measure("index.html").toFixed(2)} KiB`)
console.log("")

if (write) {
  const slack = Number(budget.slack_kib ?? SLACK_KIB)
  const routes = {}
  for (const key of pageKeys) routes[key] = Number((measure(key) + slack).toFixed(2))
  const payload = {
    note: "前端路由体积预算（gzip -9，仅 JS，单位 KiB）。由 frontend/scripts/bundle-budget.mjs --write-budget 生成，调整页面体积后需同步刷新，并在提交说明里写清原因。",
    slack_kib: slack,
    acceptance: budget.acceptance,
    routes,
  }
  writeFileSync(BUDGET_PATH, `${JSON.stringify(payload, null, 2)}\n`, "utf8")
  console.log(`[budget] 已写入 ${relative(process.cwd(), BUDGET_PATH)}（${pageKeys.length} 条路由，余量 ${slack} KiB）`)
  process.exit(0)
}

const failures = []
const entries = pageKeys.map((key) => [key, measure(key)])
entries.sort((a, b) => b[1] - a[1])

console.log(`${"路由".padEnd(34)}${"实测".padStart(9)}${"预算".padStart(9)}${"余量".padStart(9)}`)
for (const [key, size] of entries) {
  const name = key.replace(/^src\/pages\//, "").replace(/\.jsx$/, "")
  const limit = budget.routes?.[key]
  if (limit === undefined) {
    console.log(`${name.padEnd(34)}${size.toFixed(2).padStart(9)}${"未登记".padStart(9)}${"-".padStart(9)}`)
    failures.push(`${key} 未登记预算（执行 npm run bundle:budget 并说明原因）`)
    continue
  }
  const headroom = Number(limit) - size
  console.log(`${name.padEnd(34)}${size.toFixed(2).padStart(9)}${Number(limit).toFixed(2).padStart(9)}${`${headroom >= 0 ? "+" : ""}${headroom.toFixed(2)}`.padStart(9)}`)
  if (headroom < 0) failures.push(`${key} 超出预算 ${Math.abs(headroom).toFixed(2)} KiB（${size.toFixed(2)} > ${Number(limit).toFixed(2)}）`)
}
for (const key of Object.keys(budget.routes || {})) {
  if (!pageKeys.includes(key)) console.log(`[提示] 预算里有已不存在的路由：${key}（可执行 npm run bundle:budget 清理）`)
}
console.log("")

for (const item of budget.acceptance) {
  const size = measure(item.key)
  const ok = size <= Number(item.max_kib)
  console.log(`[验收] ${item.route.padEnd(18)} JS ${size.toFixed(2).padStart(7)} KiB / 目标 ≤${item.max_kib} KiB → ${ok ? "达标" : "超标"}`)
  if (!ok) failures.push(`${item.route} 超出验收目标（${size.toFixed(2)} > ${item.max_kib}）`)
}

if (!check) process.exit(0)
console.log("")
if (failures.length) {
  console.error(`[预算检查] 失败 ${failures.length} 项：`)
  for (const line of failures) console.error(`  - ${line}`)
  process.exit(1)
}
console.log("[预算检查] 通过")
