export const USER_ROLES = ["STUDENT", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN", "SYS_ADMIN"]
export const DEADLINES = [["self_deadline", "学生自查截止"], ["branch_deadline", "支部初审截止"], ["cross_deadline", "交叉互查截止"], ["college_deadline", "学院复审截止"], ["org_deadline", "组织部备案截止"]]

export function validDate(value) {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value
}

export function jsonObject(value, label) {
  let parsed
  try { parsed = typeof value === "string" ? JSON.parse(value || "{}") : value } catch { throw new Error(`${label}须为合法 JSON`) }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error(`${label}须为 JSON 对象`)
  return parsed
}

export function manageableOrgs(orgs, actor) {
  return orgs.filter((org) => actor?.role !== "COLLEGE_REVIEWER" || Number(org.id) === Number(actor.org_id) || (org.org_type === "BRANCH" && Number(org.parent_id) === Number(actor.org_id)))
}

export function normalizeGrants(rows, orgs, actor) {
  if (!rows?.length) throw new Error("请至少保留一条身份授权")
  const available = manageableOrgs(orgs, actor)
  const seen = new Set()
  return rows.map((row) => {
    const org_id = Number(row.org_id)
    const org = available.find((o) => Number(o.id) === org_id)
    if (!USER_ROLES.includes(row.role) || !org) throw new Error("请为每条授权选择有管理权限的组织和有效角色")
    if (actor?.role === "COLLEGE_REVIEWER" && ["ORG_ADMIN", "SYS_ADMIN"].includes(row.role)) throw new Error("学院审核员不能授予管理员角色")
    const key = `${row.role}@${org_id}`
    if (seen.has(key)) throw new Error("同一组织的角色授权不能重复")
    seen.add(key)
    return { role: row.role, org_id }
  })
}

export function batchPayload(form) {
  if (!form.name?.trim()) throw new Error("请填写批次名称")
  if (!Number.isInteger(Number(form.year)) || Number(form.year) < 1900 || Number(form.year) > 9999) throw new Error("年度无效")
  if (!validDate(form.start_date) || !validDate(form.end_date) || form.end_date < form.start_date) throw new Error("请填写有效的批次起止日期，结束不能早于开始")
  const stage_codes = [...new Set(String(form.stage_codes || "").split(/[,，\s]+/).filter(Boolean).map(Number))]
  if (!stage_codes.length || stage_codes.some((n) => !Number.isInteger(n) || n < 1 || n > 5)) throw new Error("阶段须为 1 至 5，以逗号分隔")
  const body = { name: form.name.trim(), year: Number(form.year), term: form.term || "FULL_YEAR", stage_codes, start_date: form.start_date, end_date: form.end_date, description: form.description || "" }
  if (form.id) body.status = form.status || "ACTIVE"
  for (const [key, label] of DEADLINES) {
    const value = String(form[key] || "").slice(0, 10)
    if (value && !validDate(value)) throw new Error(`${label}日期无效`)
    body[key] = value || null
  }
  return body
}
