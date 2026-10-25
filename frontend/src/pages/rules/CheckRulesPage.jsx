import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable from "../../components/common/DataTable"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import JsonEditor from "../../components/common/JsonEditor"
import { useRequest } from "../../hooks/useRequest"
import { checkRules } from "../../api/rules"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { severityName } from "../../utils/format"
import { can } from "../../utils/permissions"
import { useToast } from "../../context/ToastContext"

const ENGINE_NAME = { RULE: "规则引擎", LLM: "大模型", RULE_LLM: "规则与大模型" }

export default function CheckRulesPage() {
  const toast = useToast()
  const meta = useMeta()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const [cat, setCat] = useState("FORMAT")
  const req = useRequest(() => checkRules.list({ category: cat, page_size: 200 }), [cat])
  const [edit, setEdit] = useState(null)
  const [params, setParams] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const rows = req.data?.items || req.data || []

  const open = (row) => {
    setEdit(row || { category: cat, engine: "RULE", severity: "WARN", is_active: true })
    setParams(row?.params || {})
  }

  const save = async () => {
    if (!params) { toast.error("参数 JSON 无效"); return }
    const body = { ...edit, params, is_active: edit.is_active !== false, needs_human_judgement: !!edit.needs_human_judgement, is_optional: !!edit.is_optional }
    if (edit.id) await checkRules.update(edit.id, body)
    else await checkRules.create(body)
    toast.success("已保存")
    setEdit(null)
    req.reload()
  }

  return (
    <div>
      <PageHeader title="形式与内容规则" extra={writable && <button type="button" className="btn btn-primary btn-sm" onClick={() => open(null)}>新增</button>} />
      <div className="mb-3 flex gap-2">
        {[["FORMAT", "形式规范"], ["CONTENT", "内容规范"]].map(([k, label]) => (
          <button key={k} type="button" className={`btn btn-sm ${cat === k ? "btn-primary" : "btn-ghost"}`} onClick={() => setCat(k)}>{label}</button>
        ))}
      </div>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={rows} empty={cat === "FORMAT" ? "还没有形式规范规则" : "还没有内容规范规则"} columns={[
          {
            key: "name",
            title: "规则名称",
            render: (r) => (
              <div className="leading-tight">
                <div className="font-medium">{r.name}</div>
                <div className="mono mt-0.5 text-[11px] font-normal text-base-content/40">{r.code}</div>
              </div>
            ),
          },
          { key: "engine", title: "引擎", render: (r) => <span className="text-xs text-base-content/70">{ENGINE_NAME[r.engine] || r.engine || "—"}</span> },
          { key: "sev", title: "级别", render: (r) => {
            const s = r.severity
            const cls = s === "BLOCK" ? "badge-error" : s === "WARN" ? "badge-warning" : "badge-ghost"
            return s ? <span className={`badge badge-sm badge-soft whitespace-nowrap ${cls}`}>{severityName(meta, s)}</span> : "—"
          } },
          { key: "judge", title: "研判", render: (r) => (r.needs_human_judgement ? "是" : "—") },
          { key: "on", title: "启用", render: (r) => writable ? (
            <input type="checkbox" className="toggle toggle-xs" checked={r.is_active !== false} aria-label="启停" onChange={async (e) => { await checkRules.update(r.id, { is_active: e.target.checked }); req.reload() }} />
          ) : (r.is_active === false ? "停用" : "启用") },
          { key: "op", title: "", render: (r) => writable && (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => open(r)}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
      </div>
      <Modal open={!!edit} wide title={edit?.id ? "编辑规则" : "新增规则"} onClose={() => setEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={save}>保存</button>
        </>
      }>
        {edit && (
          <div className="grid gap-2 sm:grid-cols-2">
            <input className="input input-bordered input-sm" placeholder="编码" disabled={!!edit.id} value={edit.code || ""} onChange={(e) => setEdit({ ...edit, code: e.target.value })} />
            <input className="input input-bordered input-sm" placeholder="名称" value={edit.name || ""} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
            <select className="select select-bordered select-sm" value={edit.category} onChange={(e) => setEdit({ ...edit, category: e.target.value })}>
              <option value="FORMAT">形式</option><option value="CONTENT">内容</option>
            </select>
            <select className="select select-bordered select-sm" value={edit.engine || "RULE"} onChange={(e) => setEdit({ ...edit, engine: e.target.value })}>
              <option value="RULE">规则</option><option value="LLM">大模型</option><option value="RULE_LLM">混合</option>
            </select>
            <select className="select select-bordered select-sm" value={edit.severity || "WARN"} onChange={(e) => setEdit({ ...edit, severity: e.target.value })}>
              <option value="BLOCK">阻断</option><option value="WARN">警告</option><option value="INFO">提示</option>
            </select>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="checkbox checkbox-xs" checked={!!edit.needs_human_judgement} onChange={(e) => setEdit({ ...edit, needs_human_judgement: e.target.checked })} />需人工研判</label>
            <textarea className="textarea textarea-bordered text-xs sm:col-span-2" rows={2} placeholder="规则依据" value={edit.basis || ""} onChange={(e) => setEdit({ ...edit, basis: e.target.value })} />
            <textarea className="textarea textarea-bordered text-xs sm:col-span-2" rows={2} placeholder="提示文案" value={edit.message_template || ""} onChange={(e) => setEdit({ ...edit, message_template: e.target.value })} />
            <div className="sm:col-span-2"><JsonEditor value={params || {}} onChange={setParams} rows={6} /></div>
          </div>
        )}
      </Modal>
      <ConfirmDialog open={!!removeId} danger title="删除规则" message="确认删除？" onClose={() => setRemoveId(null)} onConfirm={async () => { await checkRules.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
