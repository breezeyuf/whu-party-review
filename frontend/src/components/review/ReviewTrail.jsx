import { fmtDateTime, levelName } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"
import { StatusBadge } from "../common/Badges"

export default function ReviewTrail({ records = [] }) {
  const meta = useMeta()
  if (!records.length) return <p className="text-sm text-base-content/50">还没有审核记录。</p>
  return (
    <ul className="space-y-2">
      {records.map((r) => (
        <li key={r.id || `${r.created_at}-${r.action}`} className="surface-card p-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium">{levelName(meta, r.level) || r.kind || r.action}</span>
            <StatusBadge code={r.action || r.to_status} />
            {r.is_batch && <span className="badge badge-ghost badge-xs">批量</span>}
            <span className="text-xs text-base-content/50">{fmtDateTime(r.created_at || r.time)}</span>
          </div>
          <div className="mt-1 text-xs text-base-content/70">
            {r.reviewer_name || r.actor_name || ""} {r.reviewer_role ? `· ${r.reviewer_role}` : ""}
            {r.title ? ` · ${r.title}` : ""}
          </div>
          {(r.comment || r.detail) && <p className="mt-1 text-xs">{r.comment || r.detail}</p>}
        </li>
      ))}
    </ul>
  )
}
