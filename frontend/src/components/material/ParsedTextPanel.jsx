import { useEffect, useRef, useState } from "react"
import { fmtDate } from "../../utils/format"
import { timeNodes } from "../../api/rules"
import { useRequest } from "../../hooks/useRequest"
import { extractionChanges, extractionDraft } from "../../utils/extractionWorkflow"

export default function ParsedTextPanel({ parsed, editable, onSave }) {
  const [text, setText] = useState("")
  const [fields, setFields] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [drafts, setDrafts] = useState([])
  const [reason, setReason] = useState("")
  const nextKey = useRef(0)
  const defsReq = useRequest(() => timeNodes.list(), [editable], { immediate: !!editable })
  const definitions = defsReq.data || []

  useEffect(() => {
    setText(parsed?.corrected_text ?? parsed?.full_text ?? "")
    const f = parsed?.corrected_fields ?? parsed?.extracted_fields ?? {}
    setFields(JSON.stringify(f, null, 2))
    setDrafts((parsed?.extractions || []).map((ex) => extractionDraft(ex)))
    setReason("")
    setError("")
  }, [parsed])

  if (!parsed) return <p className="text-sm text-base-content/50">解析尚未完成。</p>

  const save = async (recheck) => {
    if (busy || !editable) return
    setBusy(true)
    setError("")
    let corrected_fields
    try {
      corrected_fields = JSON.parse(fields)
      if (!corrected_fields || Array.isArray(corrected_fields) || typeof corrected_fields !== "object") throw new Error()
    } catch { setError("抽取字段必须是合法的 JSON 对象"); setBusy(false); return }
    try {
      const changes = extractionChanges(parsed.extractions || [], drafts, definitions)
      if (changes.length && !reason.trim()) throw new Error("请填写时间节点校正原因")
      await onSave({ version_id: parsed.version_id, corrected_text: text, corrected_fields, recheck, ...(changes.length ? { extractions: changes, reason: reason.trim() } : {}) })
    } catch (e) {
      setError(e.message || "保存失败")
    } finally {
      setBusy(false)
    }
  }

  const changeDraft = (key, patch) => setDrafts((rows) => rows.map((row) => row.key === key ? { ...row, ...patch } : row))
  const pending = drafts.some((draft) => draft.deleted || !draft.extraction_id || JSON.stringify(draft) !== JSON.stringify(extractionDraft((parsed.extractions || []).find((ex) => ex.id === draft.extraction_id) || {})))

  return (
    <div className="space-y-3">
      {(parsed.warnings || []).map((w, i) => <div key={i} className="alert alert-warning py-2 text-xs">{typeof w === "string" ? w : w.message}</div>)}
      <div className="text-xs text-base-content/55">解析器 {parsed.parser || "—"} · OCR {parsed.ocr_engine || "未启用"} · {parsed.page_count || 0} 页</div>
      <label className="form-control">
        <span className="label-text text-xs">解析文本</span>
        <textarea className="textarea textarea-bordered font-mono text-xs" rows={10} value={text} readOnly={!editable || busy} onChange={(e) => setText(e.target.value)} />
      </label>
      <label className="form-control">
        <span className="label-text text-xs">抽取字段（JSON）</span>
        <textarea className="textarea textarea-bordered font-mono text-xs" rows={6} value={fields} readOnly={!editable || busy} onChange={(e) => setFields(e.target.value)} />
      </label>
      <div>
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2"><h3 className="text-sm font-medium">时间节点抽取</h3>
          {editable && <button type="button" className="btn btn-outline btn-xs" disabled={busy || !definitions.some((def) => def.is_active !== false && def.value_kind !== "DERIVED")} onClick={() => setDrafts((rows) => [...rows, extractionDraft({}, `new-${++nextKey.current}`)])}>新增节点记录</button>}
        </div>
        {editable && <p className="mb-2 text-xs text-base-content/60">逐条校正这份材料的来源记录；删除会停用记录并保留审计。保存后需重新校验报告。</p>}
        {editable && defsReq.loading && <p className="text-xs" role="status">正在加载节点定义…</p>}
        {editable && defsReq.error && <p className="text-xs text-error" role="alert">节点定义加载失败，暂不能编辑记录。<button type="button" className="link" onClick={() => defsReq.reload().catch(() => {})}>重试加载节点定义</button></p>}
        {editable && definitions.length > 0 ? <div className="space-y-2">
          {drafts.map((draft, index) => {
            const def = definitions.find((item) => item.code === draft.node_code)
            const source = (parsed.extractions || []).find((ex) => ex.id === draft.extraction_id)
            return <fieldset key={draft.key} disabled={busy} className={`rounded border p-3 ${draft.deleted ? "border-warning bg-warning/5" : "border-base-300"}`} aria-label={`节点记录 ${index + 1}`}>
              <div className="mb-2 flex items-center justify-between gap-2"><span className="text-xs font-medium">记录 {index + 1}{source ? ` · ${source.method === "MANUAL" ? "人工校正" : "自动抽取"}` : " · 新增"}</span>
                <button type="button" className="btn btn-ghost btn-xs" onClick={() => draft.extraction_id ? changeDraft(draft.key, { deleted: !draft.deleted }) : setDrafts((rows) => rows.filter((row) => row.key !== draft.key))}>{draft.deleted ? "撤销删除" : "删除记录"}</button>
              </div>
              {draft.deleted ? <p className="text-xs text-warning">{draft.node_code} 将在保存后停用。</p> : <div className="grid gap-2 sm:grid-cols-2">
                <label className="form-control text-xs"><span>节点</span><select aria-label={`记录 ${index + 1} 节点`} className="select select-bordered select-sm mt-1" value={draft.node_code} disabled={busy || !!draft.extraction_id} onChange={(event) => changeDraft(draft.key, { node_code: event.target.value, end_date: "", hours: "", seq_index: 0 })}>
                  <option value="">请选择节点</option>
                  {definitions.filter((item) => item.code === draft.node_code || (item.is_active !== false && item.value_kind !== "DERIVED")).map((item) => <option key={item.code} value={item.code}>{item.code} · {item.name}</option>)}
                  {draft.node_code && !def && <option value={draft.node_code}>{draft.node_code}（定义已移除）</option>}
                </select></label>
                <label className="form-control text-xs"><span>{def?.value_kind === "DATE_RANGE" ? "开始日期" : "日期"}</span><input aria-label={`记录 ${index + 1} 日期`} className="input input-bordered input-sm mt-1" type="date" value={draft.date} onChange={(event) => changeDraft(draft.key, { date: event.target.value })} /></label>
                {def?.value_kind === "DATE_RANGE" && <label className="form-control text-xs"><span>结束日期</span><input aria-label={`记录 ${index + 1} 结束日期`} className="input input-bordered input-sm mt-1" type="date" value={draft.end_date} onChange={(event) => changeDraft(draft.key, { end_date: event.target.value })} /></label>}
                {def?.has_hours && <label className="form-control text-xs"><span>学时</span><input aria-label={`记录 ${index + 1} 学时`} className="input input-bordered input-sm mt-1" type="number" min="0" step="any" value={draft.hours} onChange={(event) => changeDraft(draft.key, { hours: event.target.value })} /></label>}
                {def?.value_kind === "DATE_SEQ" && <label className="form-control text-xs"><span>序号（从 0 开始）</span><input aria-label={`记录 ${index + 1} 序号`} className="input input-bordered input-sm mt-1" type="number" min="0" step="1" value={draft.seq_index} onChange={(event) => changeDraft(draft.key, { seq_index: event.target.value })} /></label>}
                {source && <p className="text-xs text-base-content/60 sm:col-span-2">原文：{source.raw_text || "未记录"} · 第 {source.page_no || "—"} 页{source.invalid_reason && <span className="text-warning"> · 原抽取提示：{source.invalid_reason}</span>}</p>}
              </div>}
            </fieldset>
          })}
          {!drafts.length && <p className="text-xs text-base-content/50">未抽到节点，可新增记录。</p>}
          {pending && <label className="form-control text-xs"><span>时间节点校正原因（必填）</span><textarea aria-label="时间节点校正原因" className="textarea textarea-bordered mt-1 text-sm" rows={2} disabled={busy} value={reason} onChange={(event) => setReason(event.target.value)} placeholder="说明核对依据和修改原因" /></label>}
        </div> : <ul className="space-y-1 text-xs">
          {(parsed.extractions || []).map((ex) => (
            <li key={ex.id} className="mono">
              {ex.node_code} · {fmtDate(ex.date)} · 第 {ex.page_no || "—"} 页 · {ex.method} · {ex.raw_text}
              {ex.invalid_reason && <span className="text-error"> · {ex.invalid_reason}</span>}
            </li>
          ))}
          {!(parsed.extractions || []).length && <li className="text-base-content/50">未抽到节点</li>}
        </ul>}
      </div>
      {editable && (
        <div className="flex gap-2">
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => save(false)}>保存校正</button>
          <button type="button" className="btn btn-outline btn-sm" disabled={busy} onClick={() => save(true)}>保存并重新校验</button>
        </div>
      )}
      {error && <p role="alert" className="text-xs text-error">{error}</p>}
    </div>
  )
}
