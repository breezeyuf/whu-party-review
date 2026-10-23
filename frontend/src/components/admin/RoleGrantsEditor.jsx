import { USER_ROLES, manageableOrgs } from "../../utils/adminWorkflow"
import { useMeta } from "../../context/MetaContext"
import { roleName } from "../../utils/format"

export default function RoleGrantsEditor({ value = [], onChange, orgs, actor, disabled }) {
  const meta = useMeta()
  const choices = manageableOrgs(orgs, actor)
  const update = (index, patch) => onChange(value.map((row, i) => i === index ? { ...row, ...patch } : row))
  return <fieldset disabled={disabled} className="space-y-2 rounded border border-base-300 p-3">
    <legend className="px-1 text-sm">身份授权</legend>
    <p className="text-xs text-base-content/60">每条身份由角色和组织共同确定。修改姓名或启停账号时会保留原有授权。</p>
    {value.map((row, index) => <div key={index} className="flex flex-wrap items-end gap-2">
      <label className="form-control flex-1 text-xs">角色<select aria-label={`授权 ${index + 1} 角色`} className="select select-bordered select-sm mt-1" value={row.role} onChange={(e) => update(index, { role: e.target.value })}>{USER_ROLES.filter((code) => actor?.role !== "COLLEGE_REVIEWER" || !["ORG_ADMIN", "SYS_ADMIN"].includes(code) || row.role === code).map((code) => <option key={code} value={code}>{roleName(meta, code)}</option>)}</select></label>
      <label className="form-control flex-1 text-xs">组织<select aria-label={`授权 ${index + 1} 组织`} className="select select-bordered select-sm mt-1" value={row.org_id || ""} onChange={(e) => update(index, { org_id: e.target.value })}><option value="">选择组织</option>{choices.map((org) => <option key={org.id} value={org.id}>{org.name}{org.is_active === false ? "（停用）" : ""}</option>)}{row.org_id && !choices.some((org) => Number(org.id) === Number(row.org_id)) && <option value={row.org_id}>原授权组织 #{row.org_id}（不可管理）</option>}</select></label>
      <button type="button" className="btn btn-ghost btn-sm" aria-label={`删除授权 ${index + 1}`} onClick={() => onChange(value.filter((_, i) => i !== index))}>删除</button>
    </div>)}
    <button type="button" className="btn btn-outline btn-xs" onClick={() => onChange([...value, { role: "STUDENT", org_id: "" }])}>新增身份授权</button>
  </fieldset>
}
