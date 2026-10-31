import { severityCode } from "../../utils/reviewTerms"
import { STATUS_BADGE, SEVERITY_BADGE } from "../../utils/constants"
import { useMeta } from "../../context/MetaContext"
import { severityName, statusName, recoName, handoverName, categoryName, reviewStatusName } from "../../utils/format"

export function SeverityBadge({ code }) {
  const meta = useMeta()
  if (!code) return null
  return <span className={`badge badge-sm badge-soft inline-flex shrink-0 whitespace-nowrap ${SEVERITY_BADGE[severityCode(code)] || "badge-ghost"}`}>{severityName(meta, code)}</span>
}

export function StatusBadge({ code, map, soft = true }) {
  const meta = useMeta()
  if (!code) return <span className="text-base-content/40">—</span>
  const name = map ? (map[code] || code) : statusName(meta, code)
  return <span className={`badge badge-sm inline-flex shrink-0 whitespace-nowrap ${STATUS_BADGE[code] || "badge-ghost"} ${soft ? "badge-soft" : ""}`}>{name}</span>
}

export function RecoBadge({ code, soft = true }) {
  const meta = useMeta()
  if (!code) return <span className="text-base-content/40">—</span>
  const cls = code === "SUGGEST_RETURN" ? "badge-error" : code === "NEEDS_REVIEW" ? "badge-warning" : "badge-success"
  return <span className={`badge badge-sm inline-flex shrink-0 whitespace-nowrap ${cls} ${soft ? "badge-soft" : ""}`}>{recoName(meta, code)}</span>
}

export function HandoverBadge({ code, soft = true }) {
  const meta = useMeta()
  if (!code) return null
  const cls = code === "REQUIRED" ? "badge-warning" : code === "DONE" ? "badge-success" : "badge-ghost"
  return <span className={`badge badge-sm inline-flex shrink-0 whitespace-nowrap ${cls} ${soft ? "badge-soft" : ""}`}>{handoverName(meta, code)}</span>
}

export function CategoryBadge({ code }) {
  const meta = useMeta()
  return <span className="badge badge-outline badge-sm">{categoryName(meta, code)}</span>
}

export function ReviewStatusBadge({ code }) {
  const meta = useMeta()
  return <span className={`badge badge-sm badge-soft inline-flex shrink-0 whitespace-nowrap ${STATUS_BADGE[code] || "badge-ghost"}`}>{reviewStatusName(meta, code)}</span>
}

export function DemoBadge({ show }) {
  if (!show) return null
  return <span className="badge badge-outline badge-xs">演示数据</span>
}
