import { fmtDate } from "../../utils/format"
import { SeverityBadge } from "../common/Badges"
import { Link } from "react-router-dom"
import { timelineSourceLink } from "../../utils/archiveWorkflow"

function valueText(node) {
  const eff = node.effective || {}
  if (node.value_kind === "DATE_SEQ") {
    let items = node.items || []
    if (node.code === "T06" && (node.sources || []).length) {
      const reportSources = node.sources.filter((source) => /思想汇报/.test(source.material_title || ""))
      if (reportSources.length) items = reportSources.map((source) => ({ date: source.date }))
    }
    if (!items.length) return "未提取"
    return [...new Set(items.map((it) => it.date).filter(Boolean))].sort().map((date) => fmtDate(date)).join("、")
  }
  if (!eff.date && !eff.end_date) return "未提取"
  if (eff.end_date) return `${fmtDate(eff.date)} 至 ${fmtDate(eff.end_date)}${eff.hours ? ` · ${eff.hours} 学时` : ""}`
  return fmtDate(eff.date)
}

export default function TimelineView({ timeline, onCorrect, onLocate, hidePersonalInfo = false, allowLockedCorrection = false, hideSources = false, compact = false }) {
  const allNodes = timeline?.nodes || []
  const nodes = hidePersonalInfo
    ? allNodes.filter((node) => node.code !== "T01" && !/出生日期|出生年月/.test(node.name || ""))
    : allNodes
  const derived = timeline?.derived || []
  if (!nodes.length && !derived.length) {
    return <p className="text-sm text-base-content/50">尚未提取时间节点。上传材料并完成解析后会显示在这里。</p>
  }
  const conflictCount = nodes.filter((node) => node.has_conflict || (node.anomalies || []).some((a) => a.severity === "BLOCK")).length
  return (
    <div className={compact ? "space-y-2" : "space-y-3"}>
      {!compact && <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-base-300/70 bg-base-100 px-3 py-2 text-xs text-base-content/65">
        <span>共 {nodes.length + derived.length} 个时间节点</span>
        {conflictCount > 0
          ? <span className="badge badge-error badge-sm">{conflictCount} 项需关注</span>
          : <span className="badge badge-success badge-sm">暂未发现阻断异常</span>}
      </div>}
      <ol className={compact ? "space-y-2" : "relative space-y-3 border-l-2 border-base-300/80 pl-4 sm:pl-5"}>
      {nodes.map((node) => {
        const bad = node.has_conflict || (node.anomalies || []).some((a) => a.severity === "BLOCK")
        return (
          <li key={node.code} className="relative">
            <span className={`absolute -left-[1.42rem] top-4 h-3 w-3 rounded-full border-2 border-base-100 ring-2 ${bad ? "bg-error ring-error/20" : "bg-primary ring-primary/15"}`} />
            <div className={`surface-card overflow-hidden ${bad ? "border-error/40" : ""}`}>
              <div className="flex flex-col gap-2 p-3 sm:flex-row sm:items-center sm:justify-between sm:px-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="mono text-[11px] text-base-content/45">{node.code}</span>
                    <span className="text-sm font-semibold">{node.name}</span>
                    {node.locked && <span className="badge badge-ghost badge-xs">已锁定</span>}
                    {node.has_conflict && <span className="badge badge-error badge-xs">取值冲突</span>}
                    {node.corrected && <span className="badge badge-outline badge-xs">已校正</span>}
                  </div>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2 sm:justify-end">
                  <span className={`mono rounded-lg px-2.5 py-1 text-sm font-medium ${bad ? "bg-error/10 text-error" : "bg-base-200 text-base-content"}`}>{valueText(node)}</span>
                  {onCorrect && (!node.locked || allowLockedCorrection) && <button type="button" className="btn btn-ghost btn-xs" onClick={() => onCorrect(node)}>{node.locked ? "更正已锁定节点" : "校正"}</button>}
                </div>
              </div>
              {!hideSources && (node.sources || []).length > 0 && (
                <ul className="space-y-1 border-t border-base-200 bg-base-200/35 px-3 py-2 text-xs text-base-content/70 sm:px-4">
                  {node.sources.map((s, i) => (
                    <li key={s.extraction_id || i} className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
                      {s.material_id ? (
                        <Link className="link" to={timelineSourceLink(s)}>{s.material_title || `材料 ${s.material_id}`}</Link>
                      ) : <span>{s.material_title || "来源"}</span>}
                      <span className="mono ml-2">{fmtDate(s.date)}</span>
                      {s.version_no && <span className="ml-2">v{s.version_no}</span>}
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
                <div key={a.issue_id || a.rule_code} className="flex flex-wrap items-center gap-2 border-t border-error/15 bg-error/5 px-3 py-2 text-xs sm:px-4">
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
          <span className="absolute -left-[1.42rem] top-4 h-3 w-3 rounded-full border-2 border-base-100 bg-base-300 ring-2 ring-base-300/30" />
          <div className="surface-card flex flex-wrap items-center gap-x-2 gap-y-1 bg-base-200/45 p-3">
            <span className="mono text-[11px] text-base-content/45">{d.code}</span>
            <span className="text-sm font-medium">{d.name}</span>
            <span className="badge badge-ghost badge-xs">派生</span>
            <span className="mono rounded-lg bg-base-100 px-2 py-1 text-sm">{fmtDate(d.date)}</span>
            {d.base && <span className="text-xs text-base-content/55">由 {d.base} 计算</span>}
          </div>
        </li>
      ))}
      </ol>
    </div>
  )
}
