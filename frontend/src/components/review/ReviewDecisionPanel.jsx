import { useState } from "react"
import { ConfirmDialog } from "../common/Modal"
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
  const [pendingAction, setPendingAction] = useState(null)

  const confirmed = issues.filter((i) => i.review_status === "CONFIRMED" || i.review_status === "MODIFIED")
  const reportStale = !submission.latest_report || submission.latest_report.is_stale || ["QUEUED", "RUNNING", "FAILED"].includes(submission.ai_status)
  const needsHandover = submission.latest_report?.handover_status === "REQUIRED"
  const pendingBlocks = issues.filter((issue) => issue.severity === "BLOCK" && issue.review_status === "PENDING").length

  const wrap = async (fn) => {
    setBusy(true)
    setError("")
    try { await fn(); return true } catch (e) { setError(e.message || "操作失败"); return false } finally { setBusy(false) }
  }

  const confirmAction = async () => {
    if (!pendingAction) return
    let ok = false
    if (pendingAction === "pass") ok = await wrap(() => onPass({ level, decision: "pass", comment, report_id: submission.latest_report?.id }))
    if (pendingAction === "return") ok = await wrap(() => onReturn({ level, decision: "return", comment, issue_ids: picked, deadline: deadline || undefined, report_id: submission.latest_report?.id }))
    if (pendingAction === "file") ok = await wrap(() => onFile({ comment }))
    if (pendingAction === "handover") ok = await wrap(() => onHandover({ human_decision: decision, handover_reason: reason, issue_ids: picked }))
    if (ok) setPendingAction(null)
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
          <button type="button" className="btn btn-warning btn-sm mt-2" disabled={busy || reportStale || !reason.trim() || (decision.startsWith("OVERRIDE") && (reason.trim().length < 10 || !picked.length))} onClick={() => setPendingAction("handover")}>
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
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || reportStale || needsHandover || pendingBlocks > 0} onClick={() => setPendingAction("pass")}>
            通过
          </button>
        )}
        {can.review && (
          <button type="button" className="btn btn-outline btn-error btn-sm" disabled={busy || (!picked.length && !comment.trim())} onClick={() => setPendingAction("return")}>
            退回整改
          </button>
        )}
        {can.file && (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || reportStale || needsHandover || pendingBlocks > 0} onClick={() => setPendingAction("file")}>
            备案归档
          </button>
        )}
      </div>
      {reportStale && <p className="text-xs text-warning">报告已过期或检查未完成，请先完成 AI 检查。</p>}
      {pendingBlocks > 0 && <p className="text-xs text-error">还有 {pendingBlocks} 条阻断问题待处理，处理完成后才能通过或备案。</p>}
      {can.review && <p className="text-xs text-base-content/50">退回前请至少选择一条已确认问题，或填写审核意见。</p>}
      {!can.review && !can.file && !can.handover && <p className="text-xs text-base-content/50">当前角色在此状态下没有审核操作。</p>}
      {error && <p className="text-xs text-error">{error}</p>}
      <ConfirmDialog
        open={!!pendingAction}
        title={{ pass: "确认通过审核？", return: "确认退回整改？", file: "确认备案归档？", handover: "确认提交人工接管？" }[pendingAction] || "确认操作"}
        message={{
          pass: "通过后提交包将流转到下一审核层级。请确认已核对材料原文、问题处置和 AI 报告。",
          return: "退回后学生将收到整改通知，提交包会进入整改状态。请确认退回原因和关联问题。",
          file: "备案后本阶段将归档并锁定，无法继续修改。请确认审核材料和报告均已核验。",
          handover: "提交后将记录人工研判结论与理由，请确认选择的问题和说明准确。",
        }[pendingAction] || "请确认继续此操作。"}
        confirmText={{ pass: "确认通过", return: "确认退回", file: "确认备案", handover: "确认接管" }[pendingAction] || "确认"}
        danger={pendingAction === "return" || pendingAction === "file"}
        busy={busy}
        onClose={() => { if (!busy) setPendingAction(null) }}
        onConfirm={confirmAction}
      />
    </div>
  )
}
