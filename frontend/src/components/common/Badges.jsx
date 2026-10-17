import { STATUS_BADGE, SEVERITY_BADGE } from "../../utils/constants"
import { useMeta } from "../../context/MetaContext"
import { severityName, statusName, recoName, handoverName, categoryName, reviewStatusName } from "../../utils/format"

export function SeverityBadge({ code }) {
  const meta = useMeta()
  if (!code) return null
  return <span className={`badge badge-sm ${SEVERITY_BADGE[code] || "badge-ghost"}`}>{severityName(meta, code)}</span>
}

export function StatusBadge({ code, map }) {
  const meta = useMeta()
  if (!code) return <span className="text-base-content/40">—</span>
  const name = map ? (map[code] || code) : statusName(meta, code)
  return <span className={`badge badge-sm ${STATUS_BADGE[code] || "badge-ghost"}`}>{name}</span>
}

export function RecoBadge({ code }) {
  const meta = useMeta()
  if (!code) return <span className="text-base-content/40">—</span>
  const cls = code === "SUGGEST_RETURN" ? "badge-error" : code === "NEEDS_REVIEW" ? "badge-warning" : "badge-success"
  return <span className={`badge badge-sm ${cls}`}>{recoName(meta, code)}</span>
}

export function HandoverBadge({ code }) {
  const meta = useMeta()
  if (!code) return null
  const cls = code === "REQUIRED" ? "badge-warning" : code === "DONE" ? "badge-success" : "badge-ghost"
  return <span className={`badge badge-sm ${cls}`}>{handoverName(meta, code)}</span>
}

export function CategoryBadge({ code }) {
  const meta = useMeta()
  return <span className="badge badge-outline badge-sm">{categoryName(meta, code)}</span>
}

export function ReviewStatusBadge({ code }) {
  const meta = useMeta()
  return <span className={`badge badge-sm ${STATUS_BADGE[code] || "badge-ghost"}`}>{reviewStatusName(meta, code)}</span>
}

export function DemoBadge({ show }) {
  if (!show) return null
  return <span className="badge badge-outline badge-xs">演示数据</span>
}
