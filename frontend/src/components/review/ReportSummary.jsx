import { RecoBadge, HandoverBadge } from "../common/Badges"
import { fmtDateTime } from "../../utils/format"

export default function ReportSummary({ report }) {
  if (!report) return <p className="text-sm text-base-content/50">还没有审核报告。发起 AI 校验后在此查看。</p>
  const s = report.summary || {}
  return (
    <div className="space-y-3">
      <div className="alert text-sm">
        <span>{report.disclaimer || "AI 结论仅作审核参考，未发现问题不等于审核合格，最终结论以审核人员确认为准。"}</span>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-base-content/50">参考结论</span>
        <RecoBadge code={report.recommendation} />
        <HandoverBadge code={report.handover_status} />
        {report.effective_recommendation && report.effective_recommendation !== report.recommendation && (
          <span className="text-xs">人工结论 <RecoBadge code={report.effective_recommendation} /></span>
        )}
        {report.is_stale && <span className="badge badge-warning badge-sm">报告已过期，需重跑</span>}
      </div>
      <div className="stats stats-vertical border border-base-300 bg-base-100 sm:stats-horizontal w-full">
        <div className="stat py-2 px-4">
          <div className="stat-title text-xs">问题</div>
          <div className="stat-value text-lg">{s.total ?? 0}</div>
        </div>
        <div className="stat py-2 px-4">
          <div className="stat-title text-xs">阻断 / 警告 / 提示</div>
          <div className="stat-value text-lg">{s.by_severity?.BLOCK || 0}<span className="text-sm font-normal text-base-content/50"> / {s.by_severity?.WARN || 0} / {s.by_severity?.INFO || 0}</span></div>
        </div>
        <div className="stat py-2 px-4">
          <div className="stat-title text-xs">已核材料</div>
          <div className="stat-value text-lg">{s.materials_checked ?? "—"}</div>
        </div>
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-base-content/70 sm:grid-cols-3">
        <div>模式 {report.mode === "RULE_ONLY" ? "仅规则" : report.mode || "—"}</div>
        <div>规则版本 v{report.rule_version?.version_no ?? "—"}</div>
        <div>报告 #{report.report_no}</div>
        <div>触发 {report.trigger_type || "—"}</div>
        <div>耗时 {report.duration_ms != null ? `${report.duration_ms} ms` : "—"}</div>
        <div>完成 {fmtDateTime(report.finished_at)}</div>
      </dl>
      {report.degrade_reason && <p className="text-xs text-warning">降级说明：{report.degrade_reason}</p>}
      {(report.handover_reasons || []).length > 0 && (
        <p className="text-xs">接管原因：{report.handover_reasons.join("、")}</p>
      )}
    </div>
  )
}
