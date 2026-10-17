import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable from "../../components/common/DataTable"
import RuleFormModal from "../../components/rules/RuleFormModal"
import { ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { suggestionTemplates } from "../../api/rules"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"
import { useToast } from "../../context/ToastContext"

const VARS = "{材料名} {节点名} {实际值} {要求值} {页码} {原文} {标准写法} {规则依据}"

export default function SuggestionTemplatesPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const req = useRequest(() => suggestionTemplates.list({ page_size: 200 }), [])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const rows = req.data?.items || req.data || []

  const save = async (form) => {
    const body = { ...form, is_active: form.is_active !== false }
    if (edit?.id) await suggestionTemplates.update(edit.id, body)
    else await suggestionTemplates.create(body)
    toast.success("已保存")
    req.reload()
  }

  return (
    <div>
      <PageHeader title="修改建议模板" extra={writable && <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ is_active: true })}>新增</button>}>
        可用变量：{VARS}
      </PageHeader>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} rows={rows} columns={[
          {
            key: "title",
            title: "标题",
            render: (r) => (
              <div className="leading-tight">
                <div className="font-medium">{r.title}</div>
                <div className="mono mt-0.5 text-[11px] font-normal text-base-content/40">{r.code}</div>
              </div>
            ),
          },
          { key: "rule", title: "适用规则", render: (r) => <span className="text-xs text-base-content/70" title={r.rule_code}>{r.rule_name || r.rule_code || "—"}</span> },
          { key: "vars", title: "变量", render: (r) => <span className="text-xs">{(r.variables || []).join(" ")}</span> },
          { key: "op", title: "", render: (r) => writable && (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit(r)}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
      </div>
      <RuleFormModal open={!!edit} title="建议模板" fields={[
        { key: "code", label: "编码" },
        { key: "rule_code", label: "关联规则编码" },
        { key: "title", label: "标题", wide: true },
        { key: "template_text", label: "模板正文", type: "textarea", wide: true, rows: 6 },
        { key: "example_text", label: "示例写法", type: "textarea", wide: true },
        { key: "is_active", label: "启用", type: "checkbox" },
      ]} initial={edit || {}} onClose={() => setEdit(null)} onSubmit={save} />
      <ConfirmDialog open={!!removeId} danger title="删除模板" message="确认删除？" onClose={() => setRemoveId(null)} onConfirm={async () => { await suggestionTemplates.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
