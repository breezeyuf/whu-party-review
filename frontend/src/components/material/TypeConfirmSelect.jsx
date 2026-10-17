import { useEffect, useState } from "react"
import { useMeta } from "../../context/MetaContext"

export default function TypeConfirmSelect({ value, disabled, onConfirm }) {
  const meta = useMeta()
  const [picked, setPicked] = useState(value || "")
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    setPicked(value || "")
  }, [value])

  const save = async () => {
    if (!picked) return
    setBusy(true)
    try { await onConfirm(Number(picked)) } finally { setBusy(false) }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <select className="select select-bordered select-sm" value={picked} disabled={disabled} onChange={(e) => setPicked(e.target.value)}>
        <option value="">选择材料类型</option>
        {(meta.material_types || []).map((t) => (
          <option key={t.id || t.code} value={t.id}>{t.name}</option>
        ))}
      </select>
      <button type="button" className="btn btn-primary btn-sm" disabled={disabled || busy || !picked} onClick={save}>确认类型</button>
    </div>
  )
}
