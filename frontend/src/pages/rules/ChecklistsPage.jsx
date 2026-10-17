import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import RuleFormModal from "../../components/rules/RuleFormModal"
import { Loading, ErrorState } from "../../components/common/States"
import { ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { checklists, materialTypes } from "../../api/rules"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"
import { stageShort } from "../../utils/format"

const QUANTITY_MODE = { FIXED: "固定份数", PER_PERIOD: "按周期" }

export default function ChecklistsPage() {
  const meta = useMeta()
  const toast = useToast()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const req = useRequest(() => checklists.list(), [])
  const types = useRequest(() => materialTypes.list({ page_size: 200 }), [])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)

  const groups = Array.isArray(req.data) ? req.data : (req.data?.items || [])
  const typeOptions = (types.data?.items || types.data || []).map((t) => ({ value: t.id, label: t.name }))

  const fields = [
    { key: "stage_code", label: "阶段", type: "select", options: (meta.stages || []).map((s) => ({ value: s.code, label: s.name })) },
    { key: "material_type_id", label: "材料类型", type: "select", options: typeOptions },
    { key: "quantity_mode", label: "份数方式", type: "select", options: [{ value: "FIXED", label: "固定份数" }, { value: "PER_PERIOD", label: "按周期" }] },
    { key: "fixed_count", label: "固定份数", type: "number" },
    { key: "period_months", label: "周期（月）", type: "number" },
    { key: "period_start_node", label: "周期起点节点" },
    { key: "period_end_node", label: "周期终点节点" },
    { key: "is_required", label: "必需", type: "checkbox" },
    { key: "sort_order", label: "排序", type: "number" },
    { key: "requirement_text", label: "提交要求", type: "textarea", wide: true },
  ]

  const save = async (form) => {
    const body = {
      ...form,
      stage_code: Number(form.stage_code),
      material_type_id: Number(form.material_type_id),
      fixed_count: form.fixed_count === "" ? undefined : Number(form.fixed_count),
      period_months: form.period_months === "" ? undefined : Number(form.period_months),
      sort_order: form.sort_order === "" ? undefined : Number(form.sort_order),
      is_required: !!form.is_required,
    }
    if (edit?.id) await checklists.update(edit.id, body)
    else await checklists.create(body)
    toast.success("已保存")
    req.reload()
  }

  return (
    <div>
      <PageHeader title="材料清单" extra={writable && <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({})}>新增条目</button>}>
        按阶段维护应交材料、份数和是否必需。非组织部角色只读。
      </PageHeader>
      {req.loading && !req.data ? <Loading /> : req.error ? <ErrorState error={req.error} onRetry={req.reload} /> : (
        <div className="space-y-4">
          {groups.map((g) => (
            <section key={g.stage_code} className="surface-card overflow-x-auto">
              <h2 className="border-b border-base-300 px-3 py-2 text-sm font-medium">{g.stage_name || stageShort(meta, g.stage_code)}</h2>
              <table className="table table-sm">
                <thead><tr><th>材料</th><th>方式</th><th>份数</th><th>必需</th><th>要求</th>{writable && <th />}</tr></thead>
                <tbody>
                  {(g.items || []).map((it) => (
                    <tr key={it.id}>
                      <td>{it.material_type?.name || it.material_type_name || it.material_type_id}</td>
                      <td className="text-xs">{QUANTITY_MODE[it.quantity_mode] || it.quantity_mode}</td>
                      <td className="mono text-xs">{it.quantity_mode === "PER_PERIOD" ? `每 ${it.period_months} 月` : it.fixed_count}</td>
                      <td>{it.is_required ? "是" : "否"}</td>
                      <td className="max-w-xs text-xs text-base-content/70">{it.requirement_text}</td>
                      {writable && (
                        <td className="whitespace-nowrap">
                          <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit(it)}>编辑</button>
                          <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(it.id)}>删除</button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ))}
        </div>
      )}
      <RuleFormModal open={!!edit} title={edit?.id ? "编辑清单条目" : "新增清单条目"} fields={fields} initial={edit || {}} onClose={() => setEdit(null)} onSubmit={save} />
      <ConfirmDialog open={!!removeId} danger title="删除清单条目" message="删除后对新校验生效，已有报告不受影响。" onClose={() => setRemoveId(null)} onConfirm={async () => { await checklists.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
