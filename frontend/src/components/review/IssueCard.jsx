import { useState } from "react"
import { SeverityBadge } from "../common/Badges"

import { useMeta } from "../../context/MetaContext"
import { categoryName, reviewStatusName } from "../../utils/format"
import { issuePresentation } from "../../utils/issuePresentation"

export default function IssueCard({ issue, active, onSelect, actions, footer }) {
  const [evidenceOpen, setEvidenceOpen] = useState(false)
  const meta = useMeta()
  const display = issuePresentation(issue, meta.time_nodes || [])
  const status = issue.resolution === "RESOLVED" ? "已解决" : issue.review_status === "REJECTED" ? "已驳回" : reviewStatusName(meta, issue.review_status)
  const notes = [categoryName(meta, issue.category), status,
    issue.resolution === "UNRESOLVED" && issue.review_status !== "REJECTED" ? "复核后仍存在" : "",
    issue.needs_human_judgement ? "需人工核实" : "", issue.is_new_in_recheck ? "本轮新增" : ""].filter(Boolean)
  return (
    <article id={`issue-${issue.id}`}
      className={`surface-card cursor-pointer p-3 ${active ? "border-primary" : ""}`}
      onClick={() => onSelect?.(issue)}
      tabIndex={onSelect ? 0 : undefined}
      onKeyDown={(event) => { if (event.target === event.currentTarget && ["Enter", " "].includes(event.key)) { event.preventDefault(); onSelect?.(issue) } }}
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <SeverityBadge code={issue.severity} />
        <span className="text-xs leading-relaxed text-base-content/60">{notes.join(" · ")}</span>
      </div>
      {onSelect ? (
        <button type="button" className="mt-2 text-left text-sm font-medium hover:text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary" aria-pressed={Boolean(active)} onClick={e => { e.stopPropagation(); onSelect(issue) }}>
          {display.title}
        </button>
      ) : <h3 className="mt-2 text-sm font-medium">{display.title}</h3>}
      <p className="mt-1 text-xs leading-relaxed text-base-content/75">{display.description}</p>
      {(issue.actual_value || issue.expected_value || issue.rule_basis || issue.location?.snippet || issue.material_version_id || issue.rule_code) && <details className="plain-disclosure mt-2" onToggle={e => setEvidenceOpen(e.currentTarget.open)} onClick={(event) => event.stopPropagation()}>
        <summary className="btn btn-outline btn-xs">{evidenceOpen ? "收起依据" : "查看依据"}</summary>
        <div className="details-content">
        {issue.rule_code && <p className="mono text-xs text-base-content/55">规则 {issue.rule_code}</p>}
      {(issue.actual_value || issue.expected_value) && (
        <p className="mt-1 text-xs">
          <span className="text-base-content/50">实际 </span>{issue.actual_value || "—"}
          <span className="mx-1 text-base-content/30">/</span>
          <span className="text-base-content/50">要求 </span>{issue.expected_value || "—"}
        </p>
      )}
      {issue.rule_basis && <p className="mt-1 text-xs text-base-content/55">依据：{issue.rule_basis}</p>}
      {issue.location?.snippet && <p className="mt-1 text-xs text-base-content/60">原文：“{issue.location.snippet}”</p>}
      {issue.material_version_id && <p className="mt-1 text-xs text-base-content/60">定位版本 #{issue.material_version_id}{issue.location?.page_no ? ` · 第 ${issue.location.page_no} 页` : ""}</p>}
        </div>
      </details>}
      {issue.suggestion && (
        <div className="mt-2 rounded bg-base-200 px-2 py-1.5 text-xs">
          <span className="text-base-content/50">修改建议 </span>{display.suggestion}
        </div>
      )}
      {issue.review_note && <p className="mt-1 text-xs text-base-content/65">人工处理说明：{issue.review_note}</p>}
      {issue.response_type && <div className="mt-2 rounded bg-info/10 px-2 py-1.5 text-xs"><span className="font-medium">学生整改回复 · {issue.response_type === "MODIFIED" ? "已修改" : "情况说明"}</span><p className="mt-1 whitespace-pre-wrap">{issue.response_text || "学生已提交整改版本。"}</p></div>}
      {actions && <div className="mt-2 flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>{actions}</div>}
      {footer && <div className="mt-2" onClick={(e) => e.stopPropagation()}>{footer}</div>}
    </article>
  )
}
