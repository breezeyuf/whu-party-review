export function extractionDraft(ex, key) {
  return { key: key ?? `existing-${ex.id}`, extraction_id: ex.id, node_code: ex.node_code || "", date: ex.date || "", end_date: ex.end_date || "", hours: ex.hours ?? "", seq_index: ex.seq_index ?? 0, deleted: false }
}

function validDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const date = new Date(`${value}T00:00:00Z`)
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
}

export function extractionChanges(original, drafts, definitions) {
  const changes = []
  for (const draft of drafts) {
    const before = original.find((ex) => String(ex.id) === String(draft.extraction_id))
    if (draft.deleted) {
      if (before) changes.push({ extraction_id: before.id, delete: true })
      continue
    }
    const normalized = {
      node_code: draft.node_code,
      date: draft.date || null,
      end_date: draft.end_date || null,
      hours: draft.hours === "" ? null : Number(draft.hours),
      seq_index: Number(draft.seq_index),
    }
    if (before && Object.entries(normalized).every(([key, value]) => (before[key] ?? (key === "seq_index" ? 0 : null)) === value)) continue
    const def = definitions.find((item) => item.code === draft.node_code)
    if (!def || def.value_kind === "DERIVED" || (!before && def.is_active === false)) throw new Error("请选择有效的时间节点")
    if (!validDate(draft.date)) throw new Error(`${draft.node_code}：请填写有效日期`)
    if (draft.end_date && (!validDate(draft.end_date) || draft.end_date < draft.date)) throw new Error(`${draft.node_code}：结束日期须有效且不早于开始日期`)
    if (normalized.hours != null && (!def.has_hours || !Number.isFinite(normalized.hours) || normalized.hours < 0)) throw new Error(`${draft.node_code}：学时须为非负数`)
    if (!Number.isSafeInteger(normalized.seq_index) || normalized.seq_index < 0) throw new Error(`${draft.node_code}：序号须为非负整数`)
    changes.push({ ...(before ? { extraction_id: before.id } : {}), ...normalized })
  }
  return changes
}
