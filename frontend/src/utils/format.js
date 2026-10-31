import { severityCode } from "./reviewTerms.js"
import dayjs from "dayjs"

export function fmtDate(v) {
  if (!v) return "—"
  const d = dayjs(v)
  return d.isValid() ? d.format("YYYY-MM-DD") : String(v)
}

export function fmtDateTime(v) {
  if (!v) return "—"
  const d = dayjs(v)
  return d.isValid() ? d.format("YYYY-MM-DD HH:mm") : String(v)
}

export function fmtSize(n) {
  if (n == null) return "—"
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

export function labelOf(list, code, fallback) {
  if (code == null || code === "") return fallback ?? "—"
  const hit = (list || []).find((x) => String(x.code) === String(code) || String(x.id) === String(code))
  return hit?.name || fallback || String(code)
}

export function stageName(meta, code) {
  return labelOf(meta?.stages, code, code == null ? "—" : `阶段 ${code}`)
}

// 表格/看板里的紧凑阶段名，缺失时回退到元数据的完整名称
export const STAGE_SHORT = { 1: "申请入党", 2: "积极分子", 3: "发展对象", 4: "预备党员", 5: "转正" }

export function stageShort(meta, code) {
  if (code == null) return "—"
  return STAGE_SHORT[code] || stageName(meta, code)
}

export function roleName(meta, code) {
  return labelOf(meta?.roles, code)
}

export function statusName(meta, code) {
  return labelOf(meta?.submission_statuses, code)
}

export function severityName(meta, code) {
  return severityCode(code) === "BLOCK" ? "关键问题" : labelOf(meta?.severities, code)
}

export function categoryName(meta, code) {
  return labelOf(meta?.issue_categories, code)
}

export function reviewStatusName(meta, code) {
  return labelOf(meta?.review_statuses, code)
}

export function recoName(meta, code) {
  return labelOf(meta?.recommendations, code)
}

export function handoverName(meta, code) {
  return labelOf(meta?.handover_statuses, code)
}

export function levelName(meta, code) {
  return labelOf(meta?.levels, code)
}

export function daysLeftText(n) {
  if (n == null) return "—"
  if (n < 0) return `逾期 ${-n} 天`
  if (n === 0) return "今日截止"
  return `剩余 ${n} 天`
}

export function errMessage(err, fallback = "操作失败") {
  return err?.message || err?.response?.data?.message || fallback
}

export function issueCountsText(counts) {
  if (!counts) return "—"
  const b = counts.BLOCK || 0
  const w = counts.WARN || 0
  const i = counts.INFO || 0
  return `关键问题 ${b} · 警告 ${w} · 提示 ${i}`
}
