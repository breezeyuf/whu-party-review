import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import RuleFormModal from "../../components/rules/RuleFormModal"
import { ConfirmDialog } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { exportRules, importRules, sensitivePhrases } from "../../api/rules"
import { saveBlob } from "../../api/client"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"
import { useToast } from "../../context/ToastContext"

const MATCH_TYPE = { KEYWORD: "关键词", REGEX: "正则" }
const RISK_LEVEL = { HIGH: "高", MEDIUM: "中", LOW: "低" }
const RISK_CLASS = { HIGH: "badge-error", MEDIUM: "badge-warning", LOW: "badge-ghost" }

export default function SensitivePhrasesPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const { query, setPage } = usePagination()
  const req = useRequest(() => sensitivePhrases.list(query), [JSON.stringify(query)])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const rows = req.data?.items || []

  const save = async (form) => {
    const body = { ...form, is_active: form.is_active !== false }
    if (edit?.id) await sensitivePhrases.update(edit.id, body)
    else await sensitivePhrases.create(body)
    toast.success("已保存")
    req.reload()
  }

  return (
    <div>
      <PageHeader title="敏感表述库" extra={writable && (
        <>
          <button type="button" className="btn btn-outline btn-sm" onClick={async () => saveBlob(await exportRules("sensitive-phrases"))}>导出</button>
          <label className="btn btn-ghost btn-sm">
            导入
            <input type="file" accept=".xlsx" className="hidden" onChange={async (e) => {
              const file = e.target.files?.[0]
              if (!file) return
              try {
                const res = await importRules("sensitive-phrases", file, { dryRun: false })
                toast.success(`导入 ${res.created || 0} 条`)
                req.reload()
              } catch (err) {
                const errs = err.data?.errors || []
                toast.error(errs[0] ? `导入失败（第 ${errs[0].row} 行：${errs[0].message}）` : (err.message || "导入失败"))
              }
            }} />
          </label>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ match_type: "CONTAINS", risk_level: "REVIEW", is_active: true })}>新增</button>
        </>
      )}>
        命中后一律标记“需人工研判”，系统不对政治立场下结论。
      </PageHeader>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} rows={rows} columns={[
          { key: "phrase", title: "表述" },
          { key: "match", title: "匹配", render: (r) => <span className="text-xs text-base-content/70">{MATCH_TYPE[r.match_type] || r.match_type}</span> },
          { key: "risk", title: "风险", render: (r) => (
            r.risk_level
              ? <span className={`badge badge-sm badge-soft whitespace-nowrap ${RISK_CLASS[r.risk_level] || "badge-ghost"}`}>{RISK_LEVEL[r.risk_level] || r.risk_level}</span>
              : "—"
          ) },
          { key: "note", title: "说明", render: (r) => <span className="text-xs">{r.risk_note}</span> },
          { key: "op", title: "", render: (r) => writable && (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit(r)}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
        <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />
      </div>
      <RuleFormModal open={!!edit} title="敏感表述" fields={[
        { key: "phrase", label: "表述或正则", wide: true },
        { key: "match_type", label: "匹配方式", type: "select", options: [{ value: "CONTAINS", label: "包含" }, { value: "REGEX", label: "正则" }, { value: "EXACT", label: "完全" }] },
        { key: "category", label: "分类" },
        { key: "risk_level", label: "风险", type: "select", options: [{ value: "REVIEW", label: "需研判" }, { value: "HIGH", label: "高" }] },
        { key: "risk_note", label: "风险说明", type: "textarea", wide: true },
        { key: "suggestion", label: "建议", type: "textarea", wide: true },
        { key: "is_active", label: "启用", type: "checkbox" },
      ]} initial={edit || {}} onClose={() => setEdit(null)} onSubmit={save} />
      <ConfirmDialog open={!!removeId} danger title="删除表述" message="确认删除？" onClose={() => setRemoveId(null)} onConfirm={async () => { await sensitivePhrases.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
