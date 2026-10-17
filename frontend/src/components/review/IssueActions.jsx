import { useState } from "react"
import { actIssue } from "../../api/issues"

export default function IssueActions({ issue, onChanged }) {
  const [note, setNote] = useState("")
  const [open, setOpen] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  const run = async (action, extra = {}) => {
    if (action === "reject" && note.trim().length < 2) {
      setError("驳回必须填写理由")
      return
    }
    setBusy(true)
    setError("")
    try {
      await actIssue(issue.id, { action, note: note || undefined, ...extra })
      setOpen("")
      setNote("")
      onChanged?.()
    } catch (e) {
      setError(e.message || "操作失败")
    } finally {
      setBusy(false)
    }
  }

  if (issue.review_status === "REJECTED") {
    return <button type="button" className="btn btn-ghost btn-xs" disabled={busy} onClick={() => run("reset")}>撤销驳回</button>
  }

  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-1">
        <button type="button" className="btn btn-primary btn-xs" disabled={busy} onClick={() => run("confirm")}>确认</button>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setOpen(open === "reject" ? "" : "reject")}>驳回</button>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setOpen(open === "modify" ? "" : "modify")}>修改</button>
      </div>
      {open && (
        <div className="mt-2 space-y-2">
          <textarea className="textarea textarea-bordered textarea-xs w-full" rows={2} placeholder={open === "reject" ? "驳回理由（必填）" : "修改说明"} value={note} onChange={(e) => setNote(e.target.value)} />
          {open === "modify" && (
            <ModifyFields issue={issue} busy={busy} onSave={(patch) => run("modify", { patch, note })} />
          )}
          {open === "reject" && (
            <button type="button" className="btn btn-error btn-xs" disabled={busy} onClick={() => run("reject")}>确认驳回（误报）</button>
          )}
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
      <input className="input input-bordered input-xs w-full" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea className="textarea textarea-bordered textarea-xs w-full" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
      <textarea className="textarea textarea-bordered textarea-xs w-full" rows={2} value={suggestion} onChange={(e) => setSuggestion(e.target.value)} placeholder="修改建议" />
      <select className="select select-bordered select-xs" value={severity} onChange={(e) => setSeverity(e.target.value)}>
        <option value="BLOCK">阻断</option>
        <option value="WARN">警告</option>
        <option value="INFO">提示</option>
      </select>
      <button type="button" className="btn btn-primary btn-xs" disabled={busy} onClick={() => onSave({ title, description, suggestion, severity })}>保存修改</button>
    </div>
  )
}
