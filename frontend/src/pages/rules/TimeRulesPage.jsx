import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable from "../../components/common/DataTable"
import RuleFormModal from "../../components/rules/RuleFormModal"
import JsonEditor from "../../components/common/JsonEditor"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { timeNodes, timeRules } from "../../api/rules"
import { DSL_OPS } from "../../utils/constants"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { severityName, stageName } from "../../utils/format"

const VALUE_KIND = { DATE: "日期", DATETIME: "日期时间", NUMBER: "数值", INT: "整数", TEXT: "文本", BOOL: "是否" }
import { can } from "../../utils/permissions"
import { useToast } from "../../context/ToastContext"
import { nodePayload, stringList } from "../../utils/ruleWorkflow"

export default function TimeRulesPage() {
  const toast = useToast()
  const meta = useMeta()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const [tab, setTab] = useState("rules")
  const nodes = useRequest(() => timeNodes.list(), [])
  const rules = useRequest(() => timeRules.list(), [])
  const [nodeEdit, setNodeEdit] = useState(null)
  const [ruleEdit, setRuleEdit] = useState(null)
  const [params, setParams] = useState(null)
  const [removeId, setRemoveId] = useState(null)

  const nodeRows = nodes.data?.items || nodes.data || []
  const ruleRows = rules.data?.items || rules.data || []

  const saveNode = async (form) => {
    const body = nodePayload(form)
    if (nodeEdit?.id) await timeNodes.update(nodeEdit.id, body)
    else await timeNodes.create(body)
    toast.success("节点已保存")
    nodes.reload()
  }

  const saveRule = async (form) => {
    if (!params) throw new Error("时间规则参数 JSON 无效")
    const body = {
      ...form,
      applies_stages: String(form.applies_stages || "").split(/[,，]/).map((s) => Number(s.trim())).filter(Boolean),
      params,
      is_active: form.is_active !== false,
    }
    if (ruleEdit?.id) await timeRules.update(ruleEdit.id, body)
    else await timeRules.create(body)
    toast.success("规则已保存")
    rules.reload()
  }

  return (
    <div>
      <PageHeader
        title="时间规则"
        extra={writable && (
          tab === "nodes"
            ? <button type="button" className="btn btn-primary btn-sm" onClick={() => setNodeEdit({})}>新增</button>
            : <button type="button" className="btn btn-primary btn-sm" onClick={() => { setParams({ checks: [] }); setRuleEdit({}) }}>新增</button>
        )}
      >
        维护发展党员各阶段的时间顺序、培养周期与节点完整性要求。
      </PageHeader>
      <div role="tablist" className="tabs tabs-bordered mb-3">
        <button type="button" className={`tab ${tab === "rules" ? "tab-active" : ""}`} onClick={() => setTab("rules")}>时间规则</button>
        <button type="button" className={`tab ${tab === "nodes" ? "tab-active" : ""}`} onClick={() => setTab("nodes")}>节点定义</button>
      </div>
      {tab === "nodes" ? (
        <div className="surface-card p-2">
          <DataTable loading={nodes.loading} error={nodes.error} onRetry={nodes.reload} rows={nodeRows} empty="还没有时间节点定义" columns={[
            {
              key: "name",
              title: "名称",
              render: (r) => (
                <div className="leading-tight">
                  <div className="font-medium">{r.name}</div>
                  <div className="mono mt-0.5 text-[11px] font-normal text-base-content/40">{r.code}</div>
                </div>
              ),
            },
            { key: "kind", title: "类型", render: (r) => <span className="text-xs text-base-content/70">{VALUE_KIND[r.value_kind] || r.value_kind}</span> },
            { key: "stage", title: "阶段", render: (r) => (r.stage_code == null ? "—" : stageName(meta, r.stage_code)) },
            { key: "op", title: "", render: (r) => writable && <button type="button" className="btn btn-ghost btn-xs" onClick={() => setNodeEdit(r)}>编辑</button> },
          ]} />
        </div>
      ) : (
        <div className="surface-card p-2">
          <DataTable loading={rules.loading} error={rules.error} onRetry={rules.reload} rows={ruleRows} empty="还没有时间规则" columns={[
            {
              key: "name",
              title: "名称",
              render: (r) => (
                <div className="leading-tight">
                  <div className="font-medium">{r.name}</div>
                  <div className="mono mt-0.5 text-[11px] font-normal text-base-content/40">{r.code}</div>
                </div>
              ),
            },
            { key: "sev", title: "级别", render: (r) => {
              const s = r.severity
              const cls = s === "BLOCK" ? "badge-error" : s === "WARN" ? "badge-warning" : "badge-ghost"
              return s ? <span className={`badge badge-sm badge-soft whitespace-nowrap ${cls}`}>{severityName(meta, s)}</span> : "—"
            } },
            { key: "on", title: "状态", render: (r) => (
              writable
                ? <input type="checkbox" className="toggle toggle-xs" checked={r.is_active !== false} onChange={async (e) => { await timeRules.update(r.id, { is_active: e.target.checked }); rules.reload() }} aria-label="启停" />
                : (r.is_active === false ? "停用" : "启用")
            ) },
            { key: "op", title: "", render: (r) => writable && (
              <>
                <button type="button" className="btn btn-ghost btn-xs" onClick={() => { setParams(r.params || { checks: [] }); setRuleEdit(r) }}>编辑</button>
                <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
              </>
            ) },
          ]} />
        </div>
      )}
      <RuleFormModal
        open={!!nodeEdit}
        title={nodeEdit?.id ? "编辑节点" : "新增节点"}
        fields={[
          { key: "code", label: "编码" },
          { key: "name", label: "名称" },
          { key: "value_kind", label: "取值", type: "select", options: [{ value: "DATE", label: "日期" }, { value: "DATE_RANGE", label: "区间" }, { value: "DATE_SEQ", label: "日期序列" }, { value: "DERIVED", label: "派生日期" }] },
          { key: "stage_code", label: "所属阶段", type: "number" },
          { key: "required_from_stage", label: "从第几阶段起必需", type: "number" },
          { key: "source_material_codes", label: "来源材料编码（逗号分隔）", wide: true },
          { key: "has_hours", label: "含学时", type: "checkbox" },
          { key: "extract_keywords", label: "抽取关键词", wide: true },
          { key: "derive_expr", label: '派生表达式（仅派生日期必填，例如 {"base":"T14","offset":{"value":1,"unit":"YEAR"}}）', type: "textarea", wide: true },
          { key: "sort_order", label: "排序", type: "number" },
          { key: "is_active", label: "启用", type: "checkbox" },
        ]}
        initial={nodeEdit ? { ...nodeEdit, source_material_codes: stringList(nodeEdit.source_material_codes).join(","), extract_keywords: stringList(nodeEdit.extract_keywords).join(","), derive_expr: typeof nodeEdit.derive_expr === "string" ? nodeEdit.derive_expr : JSON.stringify(nodeEdit.derive_expr || {}, null, 2) } : { is_active: true, value_kind: "DATE" }}
        onClose={() => setNodeEdit(null)}
        onSubmit={saveNode}
      />
      <Modal open={!!ruleEdit} wide title={ruleEdit?.id ? "编辑时间规则" : "新增时间规则"} onClose={() => setRuleEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setRuleEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => saveRule(ruleEdit).then(() => setRuleEdit(null)).catch((e) => toast.error(e.message))}>保存</button>
        </>
      }>
        <div className="grid gap-2 sm:grid-cols-2">
          <input className="input input-bordered input-sm" placeholder="编码" value={ruleEdit?.code || ""} disabled={!!ruleEdit?.id} onChange={(e) => setRuleEdit({ ...ruleEdit, code: e.target.value })} />
          <input className="input input-bordered input-sm" placeholder="名称" value={ruleEdit?.name || ""} onChange={(e) => setRuleEdit({ ...ruleEdit, name: e.target.value })} />
          <select className="select select-bordered select-sm" value={ruleEdit?.severity || "BLOCK"} onChange={(e) => setRuleEdit({ ...ruleEdit, severity: e.target.value })}>
            <option value="BLOCK">阻断</option><option value="WARN">警告</option><option value="INFO">提示</option><option value="CALC">计算</option>
          </select>
          <input className="input input-bordered input-sm" placeholder="适用阶段 3,4,5" value={Array.isArray(ruleEdit?.applies_stages) ? ruleEdit.applies_stages.join(",") : (ruleEdit?.applies_stages || "")} onChange={(e) => setRuleEdit({ ...ruleEdit, applies_stages: e.target.value })} />
          <textarea className="textarea textarea-bordered text-xs sm:col-span-2" rows={2} placeholder="提示文案，可用 {T04} {实际值}" value={ruleEdit?.message_template || ""} onChange={(e) => setRuleEdit({ ...ruleEdit, message_template: e.target.value })} />
        </div>
        <details className="mt-3 rounded-lg border border-base-300 bg-base-200/40 p-3">
          <summary className="cursor-pointer text-sm font-medium">高级参数（JSON）与规则条件说明</summary>
          <p className="mt-2 text-xs text-base-content/60">下列条件名是系统识别用的配置字段，保持英文不变；括号中的说明已改为中文。</p>
          <ul className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
            {DSL_OPS.map((o) => <li key={o.op} className="min-w-0"><code className="whitespace-nowrap">{o.op}</code><span className="ml-1 text-base-content/65">{o.label}：{o.description}</span></li>)}
          </ul>
          <div className="mt-3"><JsonEditor value={params || { checks: [] }} onChange={(parsed) => setParams(parsed)} /></div>
        </details>
      </Modal>
      <ConfirmDialog open={!!removeId} danger title="删除时间规则" message="确认删除？已有报告不受影响。" onClose={() => setRemoveId(null)} onConfirm={async () => { await timeRules.remove(removeId); setRemoveId(null); rules.reload() }} />
    </div>
  )
}
