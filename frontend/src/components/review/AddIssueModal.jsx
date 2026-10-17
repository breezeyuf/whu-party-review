import { useState } from "react"
import { Modal } from "../common/Modal"
import { useMeta } from "../../context/MetaContext"

const EMPTY = { category: "CONTENT", severity: "WARN", title: "", description: "", suggestion: "", material_id: "", page_no: "", snippet: "" }

export default function AddIssueModal({ open, materials = [], onClose, onCreate }) {
  const meta = useMeta()
  const [form, setForm] = useState(EMPTY)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const save = async () => {
    if (!form.title.trim() || !form.description.trim()) { setError("请填写标题和描述"); return }
    setBusy(true)
    setError("")
    try {
      await onCreate({
        category: form.category,
        severity: form.severity,
        title: form.title.trim(),
        description: form.description.trim(),
        suggestion: form.suggestion || undefined,
        material_id: form.material_id ? Number(form.material_id) : undefined,
        location: form.page_no ? { page_no: Number(form.page_no), snippet: form.snippet || undefined } : undefined,
      })
      setForm(EMPTY)
      onClose()
    } catch (e) {
      setError(e.message || "新增失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      title="人工新增问题"
      onClose={onClose}
      footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={save}>保存</button>
        </>
      )}
    >
      <div className="grid gap-2 sm:grid-cols-2">
        <select className="select select-bordered select-sm" value={form.category} onChange={(e) => set("category", e.target.value)}>
          {(meta.issue_categories || []).map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
        <select className="select select-bordered select-sm" value={form.severity} onChange={(e) => set("severity", e.target.value)}>
          {(meta.severities || []).map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
        <input className="input input-bordered input-sm sm:col-span-2" placeholder="标题" value={form.title} onChange={(e) => set("title", e.target.value)} />
        <textarea className="textarea textarea-bordered text-sm sm:col-span-2" rows={3} placeholder="问题描述" value={form.description} onChange={(e) => set("description", e.target.value)} />
        <textarea className="textarea textarea-bordered text-sm sm:col-span-2" rows={2} placeholder="修改建议" value={form.suggestion} onChange={(e) => set("suggestion", e.target.value)} />
        <select className="select select-bordered select-sm" value={form.material_id} onChange={(e) => set("material_id", e.target.value)}>
          <option value="">关联材料（可选）</option>
          {materials.map((m) => <option key={m.id} value={m.id}>{m.title}</option>)}
        </select>
        <input className="input input-bordered input-sm" type="number" min="1" placeholder="页码" value={form.page_no} onChange={(e) => set("page_no", e.target.value)} />
        <input className="input input-bordered input-sm sm:col-span-2" placeholder="原文片段" value={form.snippet} onChange={(e) => set("snippet", e.target.value)} />
      </div>
      {error && <p className="mt-2 text-xs text-error">{error}</p>}
    </Modal>
  )
}
