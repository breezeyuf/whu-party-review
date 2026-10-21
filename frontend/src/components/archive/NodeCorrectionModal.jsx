import { useState } from "react"
import { Modal } from "../common/Modal"

export default function NodeCorrectionModal({ node, onClose, onSave }) {
  const [date, setDate] = useState(node?.effective?.date || "")
  const [endDate, setEndDate] = useState(node?.effective?.end_date || "")
  const [hours, setHours] = useState(node?.effective?.hours ?? "")
  const [reason, setReason] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  if (!node) return null

  const save = async (clear = false) => {
    if (busy) return
    if (!reason.trim()) { setError("请填写校正原因"); return }
    if (!clear && !date) { setError("请选择有效日期"); return }
    if (!clear && endDate && endDate < date) { setError("截止日期不能早于开始日期"); return }
    if (!clear && hours !== "" && (!Number.isFinite(Number(hours)) || Number(hours) < 0)) { setError("学时应为非负数"); return }
    setBusy(true)
    setError("")
    try {
      await onSave(clear ? { clear: true, reason: reason.trim() } : {
        date: date || null,
        end_date: endDate || null,
        hours: hours === "" ? null : Number(hours),
        reason: reason.trim(),
      })
      onClose()
    } catch (e) {
      setError(e.message || "保存失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open
      title={`校正 ${node.code} ${node.name}`}
      onClose={() => { if (!busy) onClose() }}
      footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => save(true)} disabled={busy}>撤销校正</button>
          <button type="button" className="btn btn-ghost btn-sm" disabled={busy} onClick={onClose}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => save(false)}>保存</button>
        </>
      )}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="form-control">
          <span className="label-text text-xs">日期</span>
          <input type="date" className="input input-bordered input-sm" value={date || ""} onChange={(e) => setDate(e.target.value)} />
        </label>
        <label className="form-control">
          <span className="label-text text-xs">截止日期（区间节点）</span>
          <input type="date" className="input input-bordered input-sm" value={endDate || ""} onChange={(e) => setEndDate(e.target.value)} />
        </label>
        <label className="form-control">
          <span className="label-text text-xs">学时</span>
          <input type="number" className="input input-bordered input-sm" value={hours} onChange={(e) => setHours(e.target.value)} />
        </label>
        <label className="form-control sm:col-span-2">
          <span className="label-text text-xs">原因（必填，写入审计）</span>
          <textarea className="textarea textarea-bordered text-sm" rows={3} value={reason} onChange={(e) => setReason(e.target.value)} />
        </label>
      </div>
      {error && <p className="mt-2 text-xs text-error">{error}</p>}
    </Modal>
  )
}
