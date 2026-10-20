import { useEffect, useState } from "react"
import { fmtDate } from "../../utils/format"

export default function ParsedTextPanel({ parsed, editable, onSave }) {
  const [text, setText] = useState("")
  const [fields, setFields] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    setText(parsed?.corrected_text ?? parsed?.full_text ?? "")
    const f = parsed?.corrected_fields ?? parsed?.extracted_fields ?? {}
    setFields(JSON.stringify(f, null, 2))
    setError("")
  }, [parsed])

  if (!parsed) return <p className="text-sm text-base-content/50">解析尚未完成。</p>

  const save = async (recheck) => {
    setBusy(true)
    setError("")
    let corrected_fields
    try {
      corrected_fields = JSON.parse(fields)
      if (!corrected_fields || Array.isArray(corrected_fields) || typeof corrected_fields !== "object") throw new Error()
    } catch { setError("抽取字段必须是合法的 JSON 对象"); setBusy(false); return }
    try {
      await onSave({ version_id: parsed.version_id, corrected_text: text, corrected_fields, recheck })
    } catch (e) {
      setError(e.message || "保存失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-3">
      {(parsed.warnings || []).map((w, i) => <div key={i} className="alert alert-warning py-2 text-xs">{typeof w === "string" ? w : w.message}</div>)}
      <div className="text-xs text-base-content/55">解析器 {parsed.parser || "—"} · OCR {parsed.ocr_engine || "未启用"} · {parsed.page_count || 0} 页</div>
      <label className="form-control">
        <span className="label-text text-xs">解析文本</span>
        <textarea className="textarea textarea-bordered font-mono text-xs" rows={10} value={text} readOnly={!editable} onChange={(e) => setText(e.target.value)} />
      </label>
      <label className="form-control">
        <span className="label-text text-xs">抽取字段（JSON）</span>
        <textarea className="textarea textarea-bordered font-mono text-xs" rows={6} value={fields} readOnly={!editable} onChange={(e) => setFields(e.target.value)} />
      </label>
      <div>
        <div className="mb-1 text-xs text-base-content/60">时间节点抽取</div>
        <ul className="space-y-1 text-xs">
          {(parsed.extractions || []).map((ex) => (
            <li key={ex.id} className="mono">
              {ex.node_code} · {fmtDate(ex.date)} · 第 {ex.page_no || "—"} 页 · {ex.method} · {ex.raw_text}
              {ex.invalid_reason && <span className="text-error"> · {ex.invalid_reason}</span>}
            </li>
          ))}
          {!(parsed.extractions || []).length && <li className="text-base-content/50">未抽到节点</li>}
        </ul>
      </div>
      {editable && (
        <div className="flex gap-2">
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => save(false)}>保存校正</button>
          <button type="button" className="btn btn-outline btn-sm" disabled={busy} onClick={() => save(true)}>保存并重新校验</button>
        </div>
      )}
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  )
}
