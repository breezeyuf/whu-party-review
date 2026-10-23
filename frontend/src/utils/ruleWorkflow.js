import { jsonObject } from "./adminWorkflow.js"

export const stringList = (value) => Array.isArray(value) ? value : String(value || "").split(/[,，\n]+/).map((s) => s.trim()).filter(Boolean)
export function nodePayload(form) {
  if (!form.code?.trim() || !form.name?.trim()) throw new Error("请填写节点编码和名称")
  if (!["DATE", "DATE_RANGE", "DATE_SEQ", "DERIVED"].includes(form.value_kind)) throw new Error("节点取值类型无效")
  const body = { ...form, code: form.code.trim(), name: form.name.trim(), has_hours: !!form.has_hours, is_active: form.is_active !== false, source_material_codes: stringList(form.source_material_codes), extract_keywords: stringList(form.extract_keywords), derive_expr: null }
  for (const key of ["stage_code", "required_from_stage"]) {
    body[key] = form[key] === "" || form[key] == null ? null : Number(form[key])
    if (body[key] != null && (!Number.isInteger(body[key]) || body[key] < 1 || body[key] > 5)) throw new Error("阶段须为 1 至 5")
  }
  body.sort_order = Number(form.sort_order || 0)
  if (!Number.isInteger(body.sort_order)) throw new Error("排序须为整数")
  if (form.value_kind === "DERIVED") {
    body.derive_expr = jsonObject(form.derive_expr, "派生表达式")
    const { base, offset } = body.derive_expr
    if (!base || !offset || !Number.isFinite(offset.value) || !["DAY", "MONTH", "YEAR"].includes(offset.unit)) throw new Error("派生表达式须包含 base 与 offset（value 数值、unit 为 DAY/MONTH/YEAR）")
  }
  delete body.id
  return body
}

export function trialOverrides(text) {
  const value = jsonObject(text, "临时规则参数")
  if (Object.keys(value).some((key) => !["time_rules", "check_rules"].includes(key))) throw new Error("临时参数只支持 time_rules 与 check_rules")
  for (const rows of Object.values(value)) {
    if (!Array.isArray(rows) || rows.length > 200) throw new Error("每组临时规则须为数组，最多 200 条")
    const seen = new Set()
    for (const row of rows) {
      if (!row || typeof row !== "object" || !row.code || seen.has(row.code)) throw new Error("规则编码不能为空或重复")
      seen.add(row.code)
      if (row.params !== undefined) jsonObject(row.params, "规则 params")
      if (row.severity !== undefined && !["BLOCK", "WARN", "INFO", "CALC"].includes(row.severity)) throw new Error("规则级别无效")
      if (row.is_active !== undefined && typeof row.is_active !== "boolean") throw new Error("is_active 须为 true 或 false")
      if (Object.keys(row).some((key) => !["code", "params", "severity", "is_active"].includes(key))) throw new Error("临时规则包含不支持的字段")
    }
  }
  return value
}
