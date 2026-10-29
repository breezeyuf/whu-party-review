import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import FilterBar from "../../components/common/FilterBar"
import RuleFormModal from "../../components/rules/RuleFormModal"
import { ConfirmDialog } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { exportRules, importRules, terms } from "../../api/rules"
import { saveBlob } from "../../api/client"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"
import { useToast } from "../../context/ToastContext"
import { useMeta } from "../../context/MetaContext"
import { severityName } from "../../utils/format"

const TERM_TYPE = { VARIANT: "异体写法", SEQUENCE: "固定顺序表述" }

export default function TermsPage() {
  const toast = useToast()
  const meta = useMeta()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => terms.list(query), [JSON.stringify(query)])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const [importMsg, setImportMsg] = useState("")
  const rows = req.data?.items || []

  const save = async (form) => {
    const body = {
      ...form,
      wrong_variants: String(form.wrong_variants || "").split(/[,，\n]/).map((s) => s.trim()).filter(Boolean),
      sequence_items: String(form.sequence_items || "").split(/[,，\n]/).map((s) => s.trim()).filter(Boolean),
      is_active: form.is_active !== false,
    }
    if (edit?.id) await terms.update(edit.id, body)
    else await terms.create(body)
    toast.success("已保存")
    req.reload()
  }

  const onImport = async (file, dry) => {
    try {
      const res = await importRules("terms", file, { mode: "upsert", dryRun: dry })
      setImportMsg(`${dry ? "预检" : "导入"}：${res.created || 0} 新增，${res.updated || 0} 更新，错误 ${(res.errors || []).length}`)
      if (!dry) req.reload()
      if ((res.errors || []).length) toast.error(res.errors[0].message)
    } catch (e) {
      const errs = e.data?.errors || []
      setImportMsg(`${dry ? "预检" : "导入"}失败：${errs.length} 处错误${errs[0] ? `（第 ${errs[0].row} 行：${errs[0].message}）` : ""}`)
      toast.error(e.message || "导入失败")
    }
  }

  return (
    <div>
      <PageHeader title="规范术语" extra={writable && (
        <>
          <button type="button" className="btn btn-sm rule-action-export" onClick={async () => saveBlob(await exportRules("terms"))}>导出</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ term_type: "VARIANT", severity: "WARN", is_active: true })}>新增</button>
        </>
      )}>
        维护政治术语的标准表述、常见错误写法及并列项顺序。
      </PageHeader>
      <FilterBar values={query} onChange={setQuery} fields={[{ key: "q", label: "检索标准表述" }]} />
      {writable && (
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <label className="btn btn-sm rule-action-import font-normal">
            预检导入
            <input type="file" accept=".xlsx" className="hidden" onChange={(e) => e.target.files?.[0] && onImport(e.target.files[0], true)} />
          </label>
          <label className="btn btn-sm rule-action-import font-normal">
            正式导入
            <input type="file" accept=".xlsx" className="hidden" onChange={(e) => e.target.files?.[0] && onImport(e.target.files[0], false)} />
          </label>
          {importMsg && <span>{importMsg}</span>}
        </div>
      )}
      <div className="surface-card p-2">
        <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={rows} empty={query.q ? "没有匹配的术语" : "还没有术语"} columns={[
          { key: "std", title: "标准表述", render: (r) => r.standard_text },
          { key: "type", title: "类型", render: (r) => <span className="text-xs text-base-content/70">{TERM_TYPE[r.term_type] || r.term_type}</span> },
          { key: "wrong", title: "错误写法", render: (r) => <span className="text-xs">{(r.wrong_variants || []).join("、")}</span> },
          { key: "sev", title: "级别", render: (r) => {
            const s = r.severity
            const cls = s === "BLOCK" ? "badge-error" : s === "WARN" ? "badge-warning" : "badge-ghost"
            return s ? <span className={`badge badge-sm badge-soft whitespace-nowrap ${cls}`}>{severityName(meta, s)}</span> : "—"
          } },
          { key: "op", title: "", render: (r) => writable && (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit({ ...r, wrong_variants: (r.wrong_variants || []).join("\n"), sequence_items: (r.sequence_items || []).join("\n") })}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
        {!req.error && <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />}
      </div>
      <RuleFormModal open={!!edit} title="术语" fields={[
        { key: "term_type", label: "类型", type: "select", options: [{ value: "VARIANT", label: "错误写法" }, { value: "SEQUENCE", label: "并列顺序" }] },
        { key: "standard_text", label: "标准表述", wide: true },
        { key: "wrong_variants", label: "错误写法（每行一条）", type: "textarea", wide: true },
        { key: "sequence_items", label: "并列项（每行一项，按正确顺序）", type: "textarea", wide: true },
        { key: "category", label: "分类" },
        { key: "severity", label: "级别", type: "select", options: [{ value: "BLOCK", label: "阻断" }, { value: "WARN", label: "警告" }, { value: "INFO", label: "提示" }] },
        { key: "note", label: "说明", wide: true },
        { key: "is_active", label: "启用", type: "checkbox" },
      ]} initial={edit || {}} onClose={() => setEdit(null)} onSubmit={save} />
      <ConfirmDialog open={!!removeId} danger title="删除术语" message="确认删除？" onClose={() => setRemoveId(null)} onConfirm={async () => { await terms.remove(removeId); setRemoveId(null); req.reload() }} />
    </div>
  )
}
