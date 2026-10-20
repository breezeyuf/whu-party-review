import { SeverityBadge, CategoryBadge, ReviewStatusBadge } from "../common/Badges"

export default function IssueCard({ issue, active, onSelect, actions, footer }) {
  return (
    <article
      className={`surface-card cursor-pointer p-3 ${active ? "border-primary" : ""}`}
      onClick={() => onSelect?.(issue)}
      tabIndex={onSelect ? 0 : undefined}
      onKeyDown={(event) => { if (event.target === event.currentTarget && ["Enter", " "].includes(event.key)) { event.preventDefault(); onSelect?.(issue) } }}
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <SeverityBadge code={issue.severity} />
        <CategoryBadge code={issue.category} />
        <ReviewStatusBadge code={issue.review_status} />
        {issue.needs_human_judgement && <span className="badge badge-warning badge-xs">需人工研判</span>}
        {issue.is_new_in_recheck && <span className="badge badge-info badge-xs">复核新增</span>}
        {issue.resolution === "RESOLVED" && <span className="badge badge-success badge-xs">已解决</span>}
        {issue.resolution === "UNRESOLVED" && <span className="badge badge-error badge-xs">未解决</span>}
      </div>
      <h3 className="mt-2 text-sm font-medium">{issue.title}</h3>
      <p className="mt-1 text-xs leading-relaxed text-base-content/75">{issue.description}</p>
      {(issue.actual_value || issue.expected_value || issue.rule_basis || issue.location?.snippet || issue.material_version_id || issue.rule_code) && <details className="service-inline-details mt-2" onClick={(event) => event.stopPropagation()}>
        <summary>查看原文依据与定位</summary>
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
          <span className="text-base-content/50">修改建议 </span>{issue.suggestion}
        </div>
      )}
      {issue.review_note && <p className="mt-1 text-xs text-base-content/65">人工处理说明：{issue.review_note}</p>}
      {issue.response_type && <div className="mt-2 rounded bg-info/10 px-2 py-1.5 text-xs"><span className="font-medium">学生整改回复 · {issue.response_type === "MODIFIED" ? "已修改" : "情况说明"}</span><p className="mt-1 whitespace-pre-wrap">{issue.response_text || "学生已提交整改版本。"}</p></div>}
      {actions && <div className="mt-2 flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>{actions}</div>}
      {footer && <div className="mt-2" onClick={(e) => e.stopPropagation()}>{footer}</div>}
    </article>
  )
}
