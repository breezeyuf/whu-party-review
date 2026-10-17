import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import RuleFormModal from "../../components/rules/RuleFormModal"
import { ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { usePagination } from "../../hooks/usePagination"
import { materialTypes } from "../../api/rules"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { can } from "../../utils/permissions"
import { stageName, stageShort } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

const FIELDS = [
  { key: "code", label: "编码" },
  { key: "name", label: "名称" },
  { key: "stage_codes", label: "适用阶段（逗号分隔，如 1,2）" },
  { key: "title_keywords", label: "识别关键词（逗号分隔）", wide: true },
  { key: "exclude_keywords", label: "排除关键词", wide: true },
  { key: "element_template", label: "内容要素模板（JSON 数组或换行）", type: "textarea", wide: true, rows: 5 },
  { key: "format_requirements", label: "形式要素（JSON）", type: "textarea", wide: true, rows: 4 },
  { key: "description", label: "说明", type: "textarea", wide: true },
  { key: "is_active", label: "启用", type: "checkbox" },
]

function asList(v) {
  if (Array.isArray(v)) return v
  if (!v) return []
  return String(v).split(/[,，]/).map((s) => s.trim()).filter(Boolean)
}

export default function MaterialTypesPage() {
  const toast = useToast()
  const meta = useMeta()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const { query, setPage } = usePagination()
  const req = useRequest(() => materialTypes.list(query), [JSON.stringify(query)])
  const [edit, setEdit] = useState(null)
  const [showCode, setShowCode] = useState(false)
  const [removeId, setRemoveId] = useState(null)
  const rows = req.data?.items || (Array.isArray(req.data) ? req.data : [])

  const toForm = (row) => row ? {
    ...row,
    stage_codes: (row.stage_codes || []).join(","),
    title_keywords: (row.title_keywords || []).join(","),
    exclude_keywords: (row.exclude_keywords || []).join(","),
    element_template: typeof row.element_template === "string" ? row.element_template : JSON.stringify(row.element_template || [], null, 2),
    format_requirements: typeof row.format_requirements === "string" ? row.format_requirements : JSON.stringify(row.format_requirements || {}, null, 2),
  } : { is_active: true }

  const save = async (form) => {
    let element_template = form.element_template
    let format_requirements = form.format_requirements
    try { element_template = JSON.parse(form.element_template || "[]") } catch { element_template = asList(form.element_template) }
    try { format_requirements = JSON.parse(form.format_requirements || "{}") } catch { /* keep string rejected by api */ }
    const body = {
      ...form,
      stage_codes: asList(form.stage_codes).map(Number),
      title_keywords: asList(form.title_keywords),
      exclude_keywords: asList(form.exclude_keywords),
      element_template,
      format_requirements,
      is_active: form.is_active !== false,
    }
    if (edit?.id) await materialTypes.update(edit.id, body)
    else await materialTypes.create(body)
    toast.success("已保存")
    req.reload()
  }

  return (
    <div>
      <PageHeader
        title="材料类型与模板"
        extra={(
          <div className="flex items-center gap-3">
            <label className="flex cursor-pointer items-center gap-1.5 text-xs text-base-content/60">
              <input type="checkbox" className="checkbox checkbox-xs" checked={showCode} onChange={(e) => setShowCode(e.target.checked)} />
              显示编码
            </label>
            {writable && <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({})}>新增类型</button>}
          </div>
        )}
      />
      <div className="surface-card p-2">
        <DataTable
          loading={req.loading}
          rows={rows}
          columns={[
            {
              key: "name",
              title: "材料名称",
              render: (r) => (
                <div className="leading-tight">
                  <div className="font-medium">{r.name}</div>
                  {showCode && <div className="mono mt-0.5 text-[11px] font-normal text-base-content/40">{r.code}</div>}
                </div>
              ),
            },
            {
              key: "stages",
              title: "适用阶段",
              render: (r) => (
                <span className="flex flex-wrap gap-1">
                  {(r.stage_codes || []).map((c) => (
                    <span key={c} className="badge badge-soft badge-sm whitespace-nowrap" title={stageName(meta, c)}>
                      {stageShort(meta, c)}
                    </span>
                  ))}
                </span>
              ),
            },
            { key: "kw", title: "识别关键词", render: (r) => <span className="text-xs text-base-content/70">{(r.title_keywords || []).slice(0, 4).join("、")}</span> },
            { key: "on", title: "状态", render: (r) => (r.is_active === false ? <span className="badge badge-ghost badge-sm">停用</span> : <span className="badge badge-success badge-sm badge-soft">启用</span>) },
            { key: "op", title: "", render: (r) => writable && (
              <>
                <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit(r)}>编辑</button>
                <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
              </>
            ) },
          ]}
        />
        <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />
      </div>
      <RuleFormModal open={!!edit} title={edit?.id ? "编辑材料类型" : "新增材料类型"} fields={edit?.id ? FIELDS.filter((f) => f.key !== "code") : FIELDS} initial={toForm(edit?.id ? edit : null)} onClose={() => setEdit(null)} onSubmit={save} />
      <ConfirmDialog open={!!removeId} danger title="删除材料类型" message="已被清单引用时后端会拒绝，可改为停用。" onClose={() => setRemoveId(null)} onConfirm={async () => { await materialTypes.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
