import { SeverityBadge, CategoryBadge, ReviewStatusBadge } from "../common/Badges"

export default function IssueCard({ issue, active, onSelect, actions, footer }) {
  return (
    <article
      className={`surface-card p-3 ${active ? "border-primary bg-primary/5" : ""}`}
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <SeverityBadge code={issue.severity} />
        <CategoryBadge code={issue.category} />
        <ReviewStatusBadge code={issue.review_status} />
        {issue.needs_human_judgement && <span className="badge badge-warning badge-xs">需人工研判</span>}
        {issue.is_new_in_recheck && <span className="badge badge-info badge-xs">复核新增</span>}
        {issue.resolution === "RESOLVED" && <span className="badge badge-success badge-xs">已解决</span>}
        {issue.resolution === "UNRESOLVED" && <span className="badge badge-error badge-xs">未解决</span>}
        {issue.rule_code && <span className="mono text-[11px] text-base-content/45">{issue.rule_code}</span>}
      </div>
      {onSelect ? (
        <button type="button" className="mt-2 text-left text-sm font-medium hover:text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary" aria-pressed={Boolean(active)} onClick={() => onSelect(issue)}>
          {issue.title} <span className="ml-1 text-xs font-normal text-base-content/45">{issue.material_id || issue.location?.material_id ? "定位材料" : "选中问题"}</span>
        </button>
      ) : <h3 className="mt-2 text-sm font-medium">{issue.title}</h3>}
      <p className="mt-1 text-xs leading-relaxed text-base-content/75">{issue.description}</p>
      {(issue.location?.page_no || issue.location?.material_id || issue.material_id) && (
        <p className="mt-1 text-xs text-base-content/50">
          {issue.location?.material_title || issue.material_title || "相关材料"}
          {issue.location?.page_no ? ` · 第 ${issue.location.page_no} 页` : ""}
        </p>
      )}
      {(issue.actual_value || issue.expected_value) && (
        <p className="mt-1 text-xs">
          <span className="text-base-content/50">实际 </span>{issue.actual_value || "—"}
          <span className="mx-1 text-base-content/30">/</span>
          <span className="text-base-content/50">要求 </span>{issue.expected_value || "—"}
        </p>
      )}
      {issue.rule_basis && <p className="mt-1 text-xs text-base-content/55">依据：{issue.rule_basis}</p>}
      {issue.suggestion && (
        <div className="mt-2 rounded bg-base-200 px-2 py-1.5 text-xs">
          <span className="text-base-content/50">修改建议 </span>{issue.suggestion}
        </div>
      )}
      {issue.location?.snippet && <p className="mt-1 text-xs text-base-content/50">原文：“{issue.location.snippet}”</p>}
      {actions && <div className="mt-2 flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>{actions}</div>}
      {footer && <div className="mt-2" onClick={(e) => e.stopPropagation()}>{footer}</div>}
    </article>
  )
}
