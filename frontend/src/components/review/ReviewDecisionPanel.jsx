import { useState } from "react"
import { useMeta } from "../../context/MetaContext"
import { levelName } from "../../utils/format"

export default function ReviewDecisionPanel({ submission, issues = [], onPass, onReturn, onFile, onHandover }) {
  const meta = useMeta()
  const can = submission?.can || {}
  const level = submission?.level
  const [comment, setComment] = useState("")
  const [deadline, setDeadline] = useState("")
  const [picked, setPicked] = useState([])
  const [decision, setDecision] = useState("CONFIRM")
  const [reason, setReason] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  const confirmed = issues.filter((i) => i.review_status === "CONFIRMED" || i.review_status === "MODIFIED")
  const reportStale = !submission.latest_report || submission.latest_report.is_stale || ["QUEUED", "RUNNING", "FAILED"].includes(submission.ai_status)
  const needsHandover = submission.latest_report?.handover_status === "REQUIRED"

  const wrap = async (fn) => {
    setBusy(true)
    setError("")
    try { await fn() } catch (e) { setError(e.message || "操作失败") } finally { setBusy(false) }
  }

  const toggle = (id) => setPicked((list) => list.includes(id) ? list.filter((x) => x !== id) : [...list, id])

  return (
    <div className="surface-card space-y-3 p-4">
      <div className="text-sm font-medium">审核结论 · {levelName(meta, level)}</div>
      {can.handover && (
        <div className="rounded border border-warning/40 bg-warning/10 p-3 text-sm">
          <div className="font-medium">待人工审核</div>
          <p className="mt-1 text-xs text-base-content/70">请填写接管原因并确认人工结论。改判须写明不少于 10 字的理由，并勾选被改判的问题。</p>
          <select className="select select-bordered select-sm mt-2" value={decision} onChange={(e) => setDecision(e.target.value)}>
            <option value="CONFIRM">维持 AI 结论</option>
            <option value="OVERRIDE_PASS">改判为可通过</option>
            <option value="OVERRIDE_RETURN">改判为须退回</option>
          </select>
          <textarea className="textarea textarea-bordered mt-2 w-full text-sm" rows={2} placeholder="接管原因" value={reason} onChange={(e) => setReason(e.target.value)} />
          <button type="button" className="btn btn-warning btn-sm mt-2" disabled={busy || reportStale || !reason.trim() || (decision.startsWith("OVERRIDE") && (reason.trim().length < 10 || !picked.length))} onClick={() => wrap(() => onHandover({ human_decision: decision, handover_reason: reason, issue_ids: picked }))}>
            提交接管
          </button>
        </div>
      )}
      <textarea className="textarea textarea-bordered w-full text-sm" rows={3} placeholder="审核意见" value={comment} onChange={(e) => setComment(e.target.value)} />
      {confirmed.length > 0 && (
        <div className="max-h-32 space-y-1 overflow-auto text-xs">
          <div className="text-base-content/50">退回时关联的已确认问题</div>
          {confirmed.map((i) => (
            <label key={i.id} className="flex items-center gap-2">
              <input type="checkbox" className="checkbox checkbox-xs" checked={picked.includes(i.id)} onChange={() => toggle(i.id)} />
              <span className="truncate">{i.title}</span>
            </label>
          ))}
        </div>
      )}
      <label className="form-control max-w-xs">
        <span className="label-text text-xs">整改截止日期</span>
        <input type="date" className="input input-bordered input-sm" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
      </label>
      <div className="flex flex-wrap gap-2">
        {can.review && level !== "ORG" && (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || reportStale || needsHandover} onClick={() => wrap(() => onPass({ level, decision: "pass", comment, report_id: submission.latest_report?.id }))}>
            通过
          </button>
        )}
        {can.review && (
          <button type="button" className="btn btn-outline btn-error btn-sm" disabled={busy} onClick={() => wrap(() => onReturn({ level, decision: "return", comment, issue_ids: picked, deadline: deadline || undefined, report_id: submission.latest_report?.id }))}>
            退回整改
          </button>
        )}
        {can.file && (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || reportStale || needsHandover} onClick={() => wrap(() => onFile({ comment }))}>
            备案归档
          </button>
        )}
      </div>
      {reportStale && <p className="text-xs text-warning">报告已过期或检查未完成，请先完成 AI 检查。</p>}
      {!can.review && !can.file && !can.handover && <p className="text-xs text-base-content/50">当前角色在此状态下没有审核操作。</p>}
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  )
}
