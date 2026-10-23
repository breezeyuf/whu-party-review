import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { ErrorState } from "../../components/common/States"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { createBatch, deleteBatch, listBatches, updateBatch } from "../../api/batches"
import { fmtDate } from "../../utils/format"
import { batchPayload, DEADLINES } from "../../utils/adminWorkflow"
import { useToast } from "../../context/ToastContext"

const EMPTY = { name: "", year: new Date().getFullYear(), term: "FULL_YEAR", stage_codes: "1,2,3,4,5", start_date: "", end_date: "", status: "ACTIVE", description: "" }
export default function BatchesPage() {
  const toast = useToast()
  const { query, setPage } = usePagination()
  const req = useRequest(() => listBatches(query), [JSON.stringify(query)])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const [closeTarget, setCloseTarget] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const set = (key, value) => setEdit((f) => ({ ...f, [key]: value }))
  const save = async () => {
    if (busy) return
    setError("")
    try {
      const body = batchPayload(edit)
      setBusy(true)
      if (edit.id) await updateBatch(edit.id, body)
      else await createBatch(body)
      setEdit(null); toast.success("批次已保存")
      req.reload().catch(() => {})
    } catch (e) { setError(e.message || "保存失败") } finally { setBusy(false) }
  }
  return <div>
    <PageHeader title="发展批次" extra={<button type="button" className="btn btn-primary btn-sm" onClick={() => { setError(""); setEdit({ ...EMPTY }) }}>新建批次</button>} />
    {req.error && <ErrorState error={req.error} onRetry={req.reload} />}
    <div className="surface-card p-2"><DataTable loading={req.loading} rows={req.data?.items || []} columns={[
      { key: "name", title: "名称", render: (r) => r.name },
      { key: "year", title: "年度", render: (r) => r.year },
      { key: "span", title: "起止", render: (r) => `${fmtDate(r.start_date)} ~ ${fmtDate(r.end_date)}` },
      { key: "n", title: "档案", render: (r) => r.archive_count ?? "—" },
      { key: "status", title: "状态", render: (r) => r.status === "CLOSED" ? "已关闭" : "进行中" },
      { key: "actions", title: "操作", render: (r) => <div className="flex flex-wrap gap-1">
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => { setError(""); setEdit({ ...r, stage_codes: (r.stage_codes || []).join(",") }) }}>编辑</button>
        {r.status !== "CLOSED" && <button type="button" className="btn btn-ghost btn-xs" onClick={() => setCloseTarget(r)}>关闭批次</button>}
        <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
      </div> },
    ]} /><Pager page={req.data?.page} total={req.data?.total} pageSize={req.data?.page_size} onPage={setPage} /></div>
    <Modal open={!!edit} wide title={edit?.id ? "编辑批次" : "新建批次"} onClose={() => { if (!busy) setEdit(null) }} footer={<><button type="button" className="btn btn-ghost btn-sm" disabled={busy} onClick={() => setEdit(null)}>取消</button><button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={save}>{busy ? "保存中…" : "保存"}</button></>}>
      {edit && <fieldset disabled={busy} className="grid gap-3 sm:grid-cols-2">
        {[["name", "批次名称", "text"], ["year", "年度", "number"], ["start_date", "开始日期", "date"], ["end_date", "结束日期", "date"], ...DEADLINES.map(([key,label]) => [key,label,"date"]), ["stage_codes", "阶段编码（1 至 5，逗号分隔）", "text"]].map(([key,label,type]) => <label key={key} className="form-control text-xs">{label}<input aria-label={label} className="input input-bordered input-sm mt-1" type={type} value={type === "date" ? String(edit[key] || "").slice(0,10) : edit[key] ?? ""} onChange={(e) => set(key,e.target.value)} /></label>)}
        <label className="form-control text-xs">学期<select aria-label="批次学期" className="select select-bordered select-sm mt-1" value={edit.term} onChange={(e) => set("term",e.target.value)}><option value="FULL_YEAR">全年</option><option value="SPRING">春季</option><option value="AUTUMN">秋季</option>{!["FULL_YEAR","SPRING","AUTUMN"].includes(edit.term) && <option value={edit.term}>{edit.term}</option>}</select></label>
        {edit.id && <label className="form-control text-xs">状态<select aria-label="批次状态" className="select select-bordered select-sm mt-1" value={edit.status} onChange={(e) => set("status",e.target.value)}><option value="ACTIVE">进行中</option><option value="CLOSED">已关闭</option></select></label>}
        <label className="form-control text-xs sm:col-span-2">说明<textarea aria-label="批次说明" className="textarea textarea-bordered mt-1 text-sm" value={edit.description || ""} onChange={(e) => set("description",e.target.value)} /></label>
      </fieldset>}
      {error && <p role="alert" className="mt-2 text-xs text-error">{error}</p>}
    </Modal>
    <ConfirmDialog open={!!closeTarget} title="关闭批次" message={`确定关闭“${closeTarget?.name || ""}”？已有档案和审核记录保留。`} onClose={() => setCloseTarget(null)} onConfirm={async () => { await updateBatch(closeTarget.id,{ status:"CLOSED" }); setCloseTarget(null); await req.reload() }} />
    <ConfirmDialog open={!!removeId} danger title="删除批次" message="已有档案的批次不能删除，请使用关闭批次。" onClose={() => setRemoveId(null)} onConfirm={async () => { await deleteBatch(removeId); setRemoveId(null); await req.reload() }} />
  </div>
}
