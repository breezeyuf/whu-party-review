import { useState } from "react"
import { ConfirmDialog } from "../common/Modal"
import { useMeta } from "../../context/MetaContext"
import { levelName } from "../../utils/format"
import { PASS_RULE_TEXT, passBlockReason, reportBlockReason, sameId } from "../../utils/review"

export default function ReviewDecisionPanel({ submission, issues = [], issuesReady = true, onPass, onReturn, onFile, onHandover }) {
  const meta = useMeta()
  const can = submission?.can || {}
  const level = submission?.level
  const [comment, setComment] = useState("")
  const [deadline, setDeadline] = useState("")
  const [picked, setPicked] = useState([])
  const [handoverPicked, setHandoverPicked] = useState([])
  const [decision, setDecision] = useState("CONFIRM")
  const [reason, setReason] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [returning, setReturning] = useState(false)
  const [pendingAction, setPendingAction] = useState(null)

  const confirmed = issues.filter((i) => i.is_active !== false && ["CONFIRMED", "MODIFIED"].includes(i.review_status))
  const handoverIssues = issues.filter((i) => i.is_active !== false && (i.source === "MANUAL" || sameId(i.report_id, submission.latest_report?.id)))
  const returnIds = picked.filter((id) => confirmed.some((i) => sameId(i.id, id)))
  const handoverIds = handoverPicked.filter((id) => handoverIssues.some((i) => sameId(i.id, id)))
  const reportReason = reportBlockReason(submission)
  const passReason = passBlockReason(submission, issues, issuesReady)
  const returnReason = !issuesReady ? "问题清单尚未完整加载，请先重试。" : (!confirmed.length && !comment.trim() ? "退回须至少关联一条已确认问题，或填写审核意见。" : "")
  const handoverReason = reportReason || (!issuesReady ? "问题清单尚未完整加载。" : !reason.trim() ? "请填写接管原因。" : decision.startsWith("OVERRIDE") && (reason.trim().length < 10 || !handoverIds.length) ? "改判须填写不少于 10 字的理由，并关联问题。" : "")

  const wrap = async (fn) => {
    setBusy(true)
    setError("")
    try { await fn(); return true } catch (e) { setError(e.message || "操作失败"); return false } finally { setBusy(false) }
  }

  const confirmAction = async () => {
    if (!pendingAction) return
    let ok = false
    if (pendingAction === "pass") ok = await wrap(() => onPass({ level, decision: "pass", comment: comment.trim(), report_id: submission.latest_report?.id }))
    if (pendingAction === "file") ok = await wrap(() => onFile({ comment: comment.trim() }))
    if (pendingAction === "handover") ok = await wrap(() => onHandover({ human_decision: decision, handover_reason: reason.trim(), issue_ids: handoverIds }))
    if (ok) setPendingAction(null)
  }

  const toggle = (setter, id) => setter((list) => list.includes(id) ? list.filter((x) => x !== id) : [...list, id])

  return (
    <div className="surface-card space-y-3 p-4">
      <h2 className="text-base font-semibold">作出审核决定 <span className="ml-2 text-sm font-normal text-base-content/60">{levelName(meta, level)}</span></h2>
      {can.handover && (
        <div className="rounded border border-warning/40 bg-warning/10 p-3 text-sm">
          <div className="font-medium">待人工审核</div>
          <p className="mt-1 text-xs text-base-content/70">请填写接管原因并确认人工结论。改判须写明不少于 10 字的理由，并勾选被改判的问题。</p>
          <select aria-label="人工接管结论" className="select select-bordered select-sm mt-2" disabled={busy} value={decision} onChange={(e) => setDecision(e.target.value)}>
            <option value="CONFIRM">维持 AI 结论</option>
            <option value="OVERRIDE_PASS">改判为可通过</option>
            <option value="OVERRIDE_RETURN">改判为须退回</option>
          </select>
          <textarea aria-label="接管原因" className="textarea textarea-bordered mt-2 w-full text-sm" disabled={busy} rows={2} placeholder="接管原因" value={reason} onChange={(e) => setReason(e.target.value)} />
          <div className="mt-2 max-h-40 space-y-1 overflow-auto text-xs">
            <p className="text-base-content/60">关联本报告问题或人工问题（改判必选，可选择待确认及已驳回的问题）</p>
            {handoverIssues.map((i) => <label key={i.id} className="flex items-center gap-2"><input type="checkbox" className="checkbox checkbox-xs" disabled={busy} checked={handoverIds.includes(i.id)} onChange={() => toggle(setHandoverPicked, i.id)} /><span>{i.title}</span></label>)}
            {!handoverIssues.length && <p>暂无可关联问题。需要改判时可先人工新增问题。</p>}
          </div>
          <button type="button" className="btn btn-warning btn-sm mt-2" disabled={busy || !!handoverReason} onClick={() => setPendingAction("handover")}>
            提交接管
          </button>
          {handoverReason && <p className="mt-1 text-xs text-warning">{handoverReason}</p>}
        </div>
      )}
      {(can.review || can.file) && <textarea aria-label="审核意见" className="textarea textarea-bordered w-full text-sm" disabled={busy} rows={3} placeholder="审核意见" value={comment} onChange={(e) => setComment(e.target.value)} />}
      {returning && can.review && confirmed.length > 0 && (
        <div className="max-h-32 space-y-1 overflow-auto text-xs">
          <div className="text-base-content/50">退回时关联的已确认问题（未勾选时关联全部 {confirmed.length} 条）</div>
          {confirmed.map((i) => (
            <label key={i.id} className="flex items-center gap-2">
              <input type="checkbox" className="checkbox checkbox-xs" disabled={busy} checked={returnIds.includes(i.id)} onChange={() => toggle(setPicked, i.id)} />
              <span className="truncate">{i.title}</span>
            </label>
          ))}
        </div>
      )}
      {returning && can.review && <label className="form-control max-w-xs">
        <span className="label-text text-xs">整改截止日期</span>
        <input type="date" className="input input-bordered input-sm" disabled={busy} value={deadline} onChange={(e) => setDeadline(e.target.value)} />
        <span className="mt-1 text-xs text-base-content/50">不填写时默认为退回后 7 天。</span>
      </label>}
      <div className="flex flex-wrap gap-2">
        {can.review && level !== "ORG" && (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || !!passReason} onClick={() => setPendingAction("pass")}>
            通过
          </button>
        )}
        {can.review && !returning && (
          <button type="button" className="btn btn-outline btn-error btn-sm" disabled={busy} onClick={() => { setReturning(true); setError("") }}>退回整改</button>
        )}
        {can.review && returning && (
          <button type="button" className="btn btn-outline btn-error btn-sm" disabled={busy || !!returnReason} onClick={() => wrap(() => onReturn({ level, decision: "return", comment: comment.trim(), issue_ids: returnIds.length ? returnIds : confirmed.map((i) => i.id), deadline: deadline || undefined, report_id: submission.latest_report?.id }))}>
            确认退回
          </button>
        )}
        {returning && <button type="button" className="btn btn-ghost btn-sm" disabled={busy} onClick={() => setReturning(false)}>取消退回</button>}
        {can.file && (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || !!passReason} onClick={() => setPendingAction("file")}>
            备案归档
          </button>
        )}
      </div>
      {(can.review || can.file) && confirmed.some((issue) => issue.severity === "BLOCK") && <p className="text-xs text-warning">仍有已确认的阻断问题，请核实处理情况后作出最终审核决定。{PASS_RULE_TEXT}</p>}
      {(can.review || can.file || can.handover) && passReason && <p className="text-xs text-warning">{passReason}</p>}
      {returning && can.review && returnReason && <p className="text-xs text-base-content/60">{returnReason}</p>}
      {!can.review && !can.file && !can.handover && <p className="text-xs text-base-content/50">当前角色在此状态下没有审核操作。</p>}
      {error && <p role="alert" className="text-xs text-error">{error}</p>}
      <ConfirmDialog
        open={!!pendingAction}
        title={{ pass: "确认通过审核？", file: "确认备案归档？", handover: "确认提交人工接管？" }[pendingAction] || "确认操作"}
        message={{
          pass: "通过后提交包将流转至下一审核层级。请确认已核对材料原文、问题处置和 AI 报告。",
          file: "备案后本阶段将归档并锁定。请确认审核材料和报告均已核验。",
          handover: "提交后将记录人工研判结论与理由，请确认选择的问题和说明准确。",
        }[pendingAction] || "请确认继续此操作。"}
        confirmText={{ pass: "确认通过", file: "确认备案", handover: "确认接管" }[pendingAction] || "确认"}
        danger={pendingAction === "file"}
        busy={busy}
        onClose={() => { if (!busy) setPendingAction(null) }}
        onConfirm={confirmAction}
      />
    </div>
  )
}
