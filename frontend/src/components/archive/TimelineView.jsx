import { Link } from "react-router-dom"
import { fmtDate } from "../../utils/format"
import { SeverityBadge } from "../common/Badges"

function valueText(node) {
  const eff = node.effective || {}
  if (node.value_kind === "DATE_SEQ") {
    const items = node.items || []
    if (!items.length) return "未提取"
    return items.map((it) => fmtDate(it.date)).join("、")
  }
  if (!eff.date && !eff.end_date) return "未提取"
  if (eff.end_date) return `${fmtDate(eff.date)} 至 ${fmtDate(eff.end_date)}${eff.hours ? ` · ${eff.hours} 学时` : ""}`
  return fmtDate(eff.date)
}

export default function TimelineView({ timeline, onCorrect, onLocate }) {
  const nodes = timeline?.nodes || []
  const derived = timeline?.derived || []
  if (!nodes.length && !derived.length) {
    return <p className="text-sm text-base-content/50">尚未提取时间节点。上传材料并完成解析后会显示在这里。</p>
  }
  return (
    <ol className="relative space-y-3 border-l border-base-300 pl-4">
      {nodes.map((node) => {
        const bad = node.has_conflict || (node.anomalies || []).some((a) => a.severity === "BLOCK")
        return (
          <li key={node.code} className="relative">
            <span className={`absolute -left-[1.35rem] top-1.5 h-2.5 w-2.5 rounded-full ${bad ? "bg-error" : "bg-primary"}`} />
            <div className={`surface-card p-3 ${bad ? "border-error/40" : ""}`}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="mono text-xs text-base-content/50">{node.code}</span>
                  <span className="ml-2 text-sm font-medium">{node.name}</span>
                  {node.locked && <span className="badge badge-ghost badge-xs ml-2">已锁定</span>}
                  {node.has_conflict && <span className="badge badge-error badge-xs ml-2">取值冲突</span>}
                  {node.corrected && <span className="badge badge-outline badge-xs ml-2">已校正</span>}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`mono text-sm ${bad ? "text-error" : ""}`}>{valueText(node)}</span>
                  {onCorrect && !node.locked && (
                    <button type="button" className="btn btn-ghost btn-xs" onClick={() => onCorrect(node)}>校正</button>
                  )}
                </div>
              </div>
              {(node.sources || []).length > 0 && (
                <ul className="mt-2 space-y-1 text-xs text-base-content/70">
                  {node.sources.map((s, i) => (
                    <li key={s.extraction_id || i}>
                      {s.material_id ? (
                        <Link className="link" to={`/materials/${s.material_id}`}>{s.material_title || `材料 ${s.material_id}`}</Link>
                      ) : <span>{s.material_title || "来源"}</span>}
                      <span className="mono ml-2">{fmtDate(s.date)}</span>
                      {s.page_no && <span className="ml-2">第 {s.page_no} 页</span>}
                      {s.raw_text && <span className="ml-2 text-base-content/50">“{s.raw_text}”</span>}
                      {onLocate && s.material_id && (
                        <button type="button" className="btn btn-ghost btn-xs ml-1" onClick={() => onLocate(s)}>定位</button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              {(node.anomalies || []).map((a) => (
                <div key={a.issue_id || a.rule_code} className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                  <SeverityBadge code={a.severity} />
                  <span className="mono text-base-content/50">{a.rule_code}</span>
                  <span>{a.message}</span>
                </div>
              ))}
            </div>
          </li>
        )
      })}
      {derived.map((d) => (
        <li key={d.code} className="relative">
          <span className="absolute -left-[1.35rem] top-1.5 h-2.5 w-2.5 rounded-full bg-base-300" />
          <div className="surface-card bg-base-200/60 p-3">
            <span className="mono text-xs text-base-content/50">{d.code}</span>
            <span className="ml-2 text-sm">{d.name}</span>
            <span className="badge badge-ghost badge-xs ml-2">派生</span>
            <span className="mono ml-3 text-sm">{fmtDate(d.date)}</span>
            {d.base && <span className="ml-2 text-xs text-base-content/50">由 {d.base} 计算</span>}
          </div>
        </li>
      ))}
    </ol>
  )
}
