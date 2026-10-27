import { useState } from "react"
import { listBatches } from "../../api/batches"
import { listOrgs } from "../../api/orgs"
import { useRequest } from "../../hooks/useRequest"
import { useAuth } from "../../context/AuthContext"
import { availableBranches } from "../../utils/archiveWorkflow"
import { jsonObject, validDate } from "../../utils/adminWorkflow"
import { ErrorState } from "../common/States"
import { loadOptions } from "../../utils/listOptions"

export function archiveProfilePayload(form) {
  if (!form.real_name.trim()) throw new Error("请填写姓名")
  if (form.birth_date && (!validDate(form.birth_date) || form.birth_date > new Date().toLocaleDateString("sv-SE"))) throw new Error("出生日期无效或晚于今天")
  return { ...Object.fromEntries(["real_name", "gender", "ethnicity", "native_place", "major", "class_name"].map((key) => [key, (form[key] || "").trim()])), birth_date: form.birth_date || null, branch_id: Number(form.branch_id), batch_id: form.batch_id ? Number(form.batch_id) : null, profile_extra: jsonObject(form.profile_extra, "扩展资料") }
}

export default function ArchiveProfileForm({ archive, onSave, onCancel }) {
  const { activeRole } = useAuth()
  const orgs = useRequest(() => listOrgs({ flat: true }), [])
  const batches = useRequest(async () => ({ items: await loadOptions(listBatches) }), [])
  const branches = availableBranches(orgs.data || [], activeRole)
  const [form, setForm] = useState(() => ({ ...archive, birth_date: archive.birth_date || "", branch_id: String(archive.branch_id || ""), batch_id: String(archive.batch_id || ""), profile_extra: JSON.stringify(archive.profile_extra || {}, null, 2) }))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }))
  const save = async () => {
    if (busy) return
    setError("")
    try {
      if (!branches.some((b) => Number(b.id) === Number(form.branch_id))) throw new Error("请选择有权限管理的支部")
      if (form.batch_id && !(batches.data?.items || []).some((b) => Number(b.id) === Number(form.batch_id))) throw new Error("请选择有效批次")
      const body = archiveProfilePayload(form)
      setBusy(true)
      await onSave(body)
    } catch (e) { setError(e.message || "保存失败") } finally { setBusy(false) }
  }
  return <div className="mt-3 space-y-3">
    {(orgs.error || batches.error) && <ErrorState error={orgs.error || batches.error} onRetry={() => Promise.allSettled([orgs.reload(), batches.reload()])} />}
    <fieldset disabled={busy} className="grid gap-2 sm:grid-cols-2">
      {[["real_name", "姓名"], ["gender", "性别"], ["ethnicity", "民族"], ["birth_date", "出生日期", "date"], ["native_place", "籍贯"], ["major", "专业"], ["class_name", "班级"]].map(([key, label, type]) => <label className="form-control text-xs" key={key}>{label}<input aria-label={label} className="input input-bordered input-sm mt-1" type={type || "text"} value={form[key] || ""} onChange={(e) => set(key, e.target.value)} /></label>)}
      <label className="form-control text-xs">所属支部<select aria-label="档案所属支部" className="select select-bordered select-sm mt-1" value={form.branch_id} onChange={(e) => set("branch_id", e.target.value)}><option value="">选择支部</option>{branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></label>
      <label className="form-control text-xs">发展批次<select aria-label="档案发展批次" className="select select-bordered select-sm mt-1" value={form.batch_id} onChange={(e) => set("batch_id", e.target.value)}><option value="">不指定批次</option>{(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></label>
      <label className="form-control text-xs sm:col-span-2">扩展资料（JSON 对象）<textarea aria-label="扩展资料" className="textarea textarea-bordered mt-1 text-xs" rows={4} value={form.profile_extra} onChange={(e) => set("profile_extra", e.target.value)} /></label>
    </fieldset>
    <p className="text-xs text-base-content/60">修改基本信息后，需重新校验相关报告。</p>
    <div className="flex gap-2"><button type="button" className="btn btn-primary btn-xs" disabled={busy || orgs.loading || batches.loading || !!orgs.error || !!batches.error} onClick={save}>{busy ? "保存中…" : "保存"}</button><button type="button" className="btn btn-ghost btn-xs" disabled={busy} onClick={onCancel}>取消</button></div>
    {error && <p role="alert" className="text-xs text-error">{error}</p>}
  </div>
}
