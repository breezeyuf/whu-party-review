import { useState } from "react"
import { actIssue } from "../../api/issues"

export default function IssueActions({ issue, onChanged, disabled = false }) {
  const [note, setNote] = useState("")
  const [open, setOpen] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  const run = async (action, extra = {}) => {
    if (action === "reject" && !note.trim()) {
      setError("驳回必须填写理由")
      return
    }
    setBusy(true)
    setError("")
    try {
      await actIssue(issue.id, { action, note: note.trim() || undefined, ...extra })
      setOpen("")
      setNote("")
      await onChanged?.()
    } catch (e) {
      setError(e.message || "操作失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-1">
        {issue.review_status === "PENDING" && <button type="button" className="btn btn-primary btn-xs" disabled={busy || disabled} onClick={() => run("confirm")}>确认问题</button>}
        {issue.review_status !== "REJECTED" && <>
          <button type="button" className="btn btn-ghost btn-xs" disabled={busy || disabled} onClick={() => { setError(""); setOpen(open === "reject" ? "" : "reject") }}>驳回误报</button>
          <button type="button" className="btn btn-ghost btn-xs" disabled={busy || disabled} onClick={() => { setError(""); setOpen(open === "modify" ? "" : "modify") }}>修改并确认</button>
        </>}
        {issue.review_status !== "PENDING" && <button type="button" className="btn btn-ghost btn-xs" disabled={busy || disabled} onClick={() => run("reset")}>{issue.review_status === "REJECTED" ? "撤销驳回" : "恢复待确认"}</button>}
      </div>
      {open && (
        <div className="mt-2 space-y-2">
          <textarea aria-label={open === "reject" ? "驳回理由" : "修改说明"} disabled={busy || disabled} className="textarea textarea-bordered textarea-xs w-full" rows={2} placeholder={open === "reject" ? "驳回理由（必填）" : "修改说明"} value={note} onChange={(e) => setNote(e.target.value)} />
          {open === "modify" && (
            <ModifyFields issue={issue} busy={busy || disabled} onSave={(patch) => run("modify", { patch })} />
          )}
          {open === "reject" && (
            <button type="button" className="btn btn-error btn-xs" disabled={busy || disabled || !note.trim()} onClick={() => run("reject")}>确认驳回（误报）</button>
          )}
          <button type="button" className="btn btn-ghost btn-xs" disabled={busy} onClick={() => { setOpen(""); setError("") }}>取消</button>
        </div>
      )}
      {error && <p className="mt-1 text-xs text-error">{error}</p>}
    </div>
  )
}

function ModifyFields({ issue, busy, onSave }) {
  const [title, setTitle] = useState(issue.title || "")
  const [description, setDescription] = useState(issue.description || "")
  const [suggestion, setSuggestion] = useState(issue.suggestion || "")
  const [severity, setSeverity] = useState(issue.severity || "WARN")
  return (
    <div className="space-y-1">
      <input aria-label="问题标题" disabled={busy} className="input input-bordered input-xs w-full" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea aria-label="问题描述" disabled={busy} className="textarea textarea-bordered textarea-xs w-full" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
      <textarea aria-label="修改建议" disabled={busy} className="textarea textarea-bordered textarea-xs w-full" rows={2} value={suggestion} onChange={(e) => setSuggestion(e.target.value)} placeholder="修改建议" />
      <select aria-label="问题级别" disabled={busy} className="select select-bordered select-xs" value={severity} onChange={(e) => setSeverity(e.target.value)}>
        <option value="BLOCK">阻断</option>
        <option value="WARN">警告</option>
        <option value="INFO">提示</option>
      </select>
      <button type="button" className="btn btn-primary btn-xs" disabled={busy || !title.trim() || !description.trim()} onClick={() => onSave({ title: title.trim(), description: description.trim(), suggestion: suggestion.trim(), severity })}>保存修改</button>
    </div>
  )
}
