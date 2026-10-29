import { fmtDateTime, levelName } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"
import { StatusBadge } from "../common/Badges"
import { Link } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"
import { reviewHistoryLink } from "../../utils/review"

const ACTIONS = { PASS: "通过", RETURN: "退回整改", FILE: "备案归档", SUBMIT: "提交审核", RESUBMIT: "整改重提" }
const KINDS = { UPLOAD: "材料上传", AI_REPORT: "AI 检查", REVIEW: "审核记录", NOTICE: "通知消息", ISSUE_RESPONSE: "整改回复", NODE_CORRECTION: "节点校正", FILED: "备案归档" }

export default function ReviewTrail({ records = [] }) {
  const meta = useMeta()
  const { activeRole } = useAuth()
  if (!records.length) return <p className="text-sm text-base-content/50">还没有历史记录。</p>
  return (
    <ul className="space-y-2">
      {records.map((r, index) => {
        const action = r.action || (["REVIEW", "FILED"].includes(r.kind) ? r.title : null)
        const target = reviewHistoryLink(r, activeRole?.role)
        return <li key={r.id != null ? `record:${r.id}` : `${r.time || r.created_at}:${r.kind}:${r.link_type}:${r.link_id}:${index}`} className="surface-card p-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium">{r.level ? levelName(meta, r.level) : KINDS[r.kind] || r.kind || "审核记录"}</span>
            {action && <StatusBadge code={action} map={ACTIONS} />}
            {r.to_status && <StatusBadge code={r.to_status} />}
            {r.is_batch && <span className="badge badge-ghost badge-xs">批量</span>}
            <span className="text-xs text-base-content/50">{fmtDateTime(r.created_at || r.time)}</span>
          </div>
          <div className="mt-1 text-xs text-base-content/70">
            {r.reviewer_name || r.actor_name || ""} {r.reviewer_role ? `· ${r.reviewer_role}` : ""}
            {r.title && !(["REVIEW", "FILED"].includes(r.kind) && ACTIONS[r.title]) ? ` · ${r.title}` : ""}
            {r.report_no ? ` · 报告 #${r.report_no}` : ""}
            {r.round_no ? ` · 第 ${r.round_no} 轮` : ""}
          </div>
          {(r.comment || r.detail) && <p className="mt-1 whitespace-pre-wrap text-xs">{r.comment || (typeof r.detail === "string" ? r.detail : JSON.stringify(r.detail))}</p>}
          {target && <Link className="link mt-2 inline-block text-xs" to={target.to}>{target.label}</Link>}
        </li>
      })}
    </ul>
  )
}
