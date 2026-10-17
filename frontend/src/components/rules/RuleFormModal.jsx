import { useEffect, useState } from "react"
import { Modal } from "../common/Modal"

export default function RuleFormModal({ open, title, fields, initial, onClose, onSubmit }) {
  const [form, setForm] = useState(initial || {})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => { setForm(initial || {}) }, [initial, open])

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const save = async () => {
    setBusy(true)
    setError("")
    try {
      await onSubmit(form)
      onClose()
    } catch (e) {
      setError(e.message || "保存失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      title={title}
      wide
      onClose={onClose}
      footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={save}>保存</button>
        </>
      )}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        {fields.map((f) => (
          <label key={f.key} className={`form-control ${f.wide ? "sm:col-span-2" : ""}`}>
            <span className="label-text text-xs">{f.label}</span>
            {f.type === "textarea" ? (
              <textarea className="textarea textarea-bordered font-mono text-xs" rows={f.rows || 4} value={form[f.key] ?? ""} onChange={(e) => set(f.key, e.target.value)} />
            ) : f.type === "select" ? (
              <select className="select select-bordered select-sm" value={form[f.key] ?? ""} onChange={(e) => set(f.key, e.target.value)}>
                <option value="">请选择</option>
                {(f.options || []).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            ) : f.type === "checkbox" ? (
              <input type="checkbox" className="toggle toggle-sm mt-2" checked={!!form[f.key]} onChange={(e) => set(f.key, e.target.checked)} />
            ) : (
              <input className="input input-bordered input-sm" type={f.type || "text"} value={form[f.key] ?? ""} onChange={(e) => set(f.key, e.target.value)} />
            )}
          </label>
        ))}
      </div>
      {error && <p className="mt-2 text-xs text-error">{error}</p>}
    </Modal>
  )
}
