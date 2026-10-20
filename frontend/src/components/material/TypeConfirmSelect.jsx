import { useEffect, useState } from "react"
import { useMeta } from "../../context/MetaContext"

export default function TypeConfirmSelect({ value, disabled, onConfirm }) {
  const meta = useMeta()
  const [picked, setPicked] = useState(value || "")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    setPicked(value || "")
    setError("")
  }, [value])

  const save = async () => {
    if (!picked) return
    setBusy(true)
    setError("")
    try { await onConfirm(Number(picked)) }
    catch (failure) { setError(failure.message || "材料类型确认失败，请重试") }
    finally { setBusy(false) }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <select aria-label="材料类型" className="select select-bordered select-sm" value={picked} disabled={disabled || busy} onChange={(e) => { setPicked(e.target.value); setError("") }}>
        <option value="">选择材料类型</option>
        {(meta.material_types || []).map((t) => (
          <option key={t.id || t.code} value={t.id}>{t.name}</option>
        ))}
      </select>
      <button type="button" className="btn btn-primary btn-sm" disabled={disabled || busy || !picked} onClick={save}>{busy ? "确认中…" : "确认类型"}</button>
      {error && <p role="alert" className="w-full text-xs text-error">{error}</p>}
    </div>
  )
}
