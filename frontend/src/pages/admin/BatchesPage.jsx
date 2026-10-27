import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { usePagination } from "../../hooks/usePagination"
import { createBatch, deleteBatch, listBatches, updateBatch } from "../../api/batches"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

const EMPTY = { name: "", year: new Date().getFullYear(), term: "FULL_YEAR", status: "PLANNED", stage_codes: "1,2,3,4,5", start_date: "", end_date: "", self_deadline: "", branch_deadline: "", cross_deadline: "", college_deadline: "", org_deadline: "", description: "" }

const TERM_NAME = { FULL_YEAR: "全年", H1: "上半年", H2: "下半年", 全年: "全年" }
const BATCH_STATUS = { PLANNED: "筹备中", ACTIVE: "进行中", CLOSED: "已结束", ARCHIVED: "已归档" }

export default function BatchesPage() {
  const toast = useToast()
  const { query, setPage, setQuery } = usePagination()
  const req = useRequest(() => listBatches(query), [JSON.stringify(query)])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [removing, setRemoving] = useState(false)
  const rows = req.data?.items || []

  const save = async () => {
    if (saving) return
    const name = String(edit.name || "").trim()
    const year = Number(edit.year)
    const stageCodes = String(edit.stage_codes || "").split(/[,，]/).map((s) => s.trim()).filter(Boolean).map(Number)
    if (!name) { toast.error("请填写批次名称"); return }
    if (!Number.isInteger(year) || year < 2000 || year > 2200) { toast.error("年度须填写 2000 至 2200 之间的整数"); return }
    if (!stageCodes.length || stageCodes.some((code) => !Number.isInteger(code) || code < 1 || code > 5) || new Set(stageCodes).size !== stageCodes.length) {
      toast.error("阶段编码须为 1 至 5，不能重复"); return
    }
    if (edit.start_date && edit.end_date && edit.start_date > edit.end_date) { toast.error("结束日期不能早于开始日期"); return }
    const deadlines = [edit.self_deadline, edit.branch_deadline, edit.cross_deadline, edit.college_deadline, edit.org_deadline].filter(Boolean)
    if (deadlines.some((date, index) => index > 0 && deadlines[index - 1] > date)) {
      toast.error("各级截止时间应按自查、支部、交叉互查、学院、组织部的顺序排列"); return
    }
    const body = {
      ...edit,
      name,
      year,
      stage_codes: stageCodes,
    }
    setSaving(true)
    try {
      if (edit.id) await updateBatch(edit.id, body)
      else await createBatch(body)
      toast.success("已保存")
      setEdit(null)
      req.reload().catch((e) => toast.error(`批次已保存，但列表刷新失败：${e.message || "请重试"}`))
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PageHeader title="发展批次" extra={<button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ ...EMPTY })}>新建批次</button>} />
      <div className="surface-card p-2">
        <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={rows} empty="还没有发展批次" emptyHint="点击右上角“新建批次”开始配置。" columns={[
          { key: "name", title: "名称", render: (r) => <>{r.name} {r.is_demo && <span className="badge badge-outline badge-xs">演示</span>}</> },
          { key: "year", title: "年度", render: (r) => `${r.year} ${TERM_NAME[r.term] || r.term || ""}` },
          { key: "span", title: "起止", render: (r) => <span className="text-xs">{fmtDate(r.start_date)} ~ {fmtDate(r.end_date)}</span> },
          { key: "n", title: "档案", render: (r) => r.archive_count ?? "—" },
          { key: "st", title: "状态", render: (r) => {
            const s = r.status
            const cls = s === "ACTIVE" ? "badge-success" : s === "CLOSED" || s === "ARCHIVED" ? "badge-ghost" : "badge-warning"
            return s ? <span className={`badge badge-sm badge-soft ${cls}`}>{BATCH_STATUS[s] || s}</span> : "—"
          } },
          { key: "op", title: "", render: (r) => (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit({ ...r, stage_codes: (r.stage_codes || []).join(",") })}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs text-error" disabled={Number(r.archive_count) > 0} title={Number(r.archive_count) > 0 ? "批次已有档案，不能删除；可编辑状态并设为已结束" : "删除批次"} onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
        {!req.error && <div className="px-2"><Pager page={req.data?.page ?? query.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })} /></div>}
      </div>
      <Modal open={!!edit} wide title={edit?.id ? "编辑批次" : "新建批次"} onClose={() => setEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" disabled={saving} onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={saving} onClick={save}>{saving ? "保存中…" : "保存"}</button>
        </>
      }>
        {edit && (
          <div className="grid gap-2 sm:grid-cols-2">
            <label className="form-control sm:col-span-2"><span className="label-text text-xs">批次名称</span><input className="input input-bordered input-sm" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">年度</span><input className="input input-bordered input-sm" type="number" min="2000" max="2200" value={edit.year} onChange={(e) => setEdit({ ...edit, year: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">学期</span><select className="select select-bordered select-sm" value={edit.term || "FULL_YEAR"} onChange={(e) => setEdit({ ...edit, term: e.target.value })}><option value="FULL_YEAR">全年</option><option value="H1">上半年</option><option value="H2">下半年</option></select></label>
            <label className="form-control"><span className="label-text text-xs">批次开始日期</span><input className="input input-bordered input-sm" type="date" value={String(edit.start_date || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, start_date: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">批次结束日期</span><input className="input input-bordered input-sm" type="date" value={String(edit.end_date || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, end_date: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">学生自查截止</span><input className="input input-bordered input-sm" type="date" value={String(edit.self_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, self_deadline: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">支部初审截止</span><input className="input input-bordered input-sm" type="date" value={String(edit.branch_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, branch_deadline: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">交叉互查截止</span><input className="input input-bordered input-sm" type="date" value={String(edit.cross_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, cross_deadline: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">学院复审截止</span><input className="input input-bordered input-sm" type="date" value={String(edit.college_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, college_deadline: e.target.value })} /></label>
            <label className="form-control"><span className="label-text text-xs">组织部备案截止</span><input className="input input-bordered input-sm" type="date" value={String(edit.org_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, org_deadline: e.target.value })} /></label>
            {edit.id ? <label className="form-control"><span className="label-text text-xs">批次状态</span><select className="select select-bordered select-sm" value={edit.status || "PLANNED"} onChange={(e) => setEdit({ ...edit, status: e.target.value })}>{Object.entries(BATCH_STATUS).map(([code, label]) => <option key={code} value={code}>{label}</option>)}</select></label> : <p className="sm:col-span-2 text-xs text-base-content/55">新建批次默认状态为“筹备中”，启用后可在编辑中调整。</p>}
            <label className="form-control sm:col-span-2"><span className="label-text text-xs">适用阶段编码（逗号分隔）</span><input className="input input-bordered input-sm" placeholder="例如 1,2,3,4,5" value={edit.stage_codes} onChange={(e) => setEdit({ ...edit, stage_codes: e.target.value })} /></label>
            <textarea className="textarea textarea-bordered text-sm sm:col-span-2" rows={2} placeholder="说明" value={edit.description || ""} onChange={(e) => setEdit({ ...edit, description: e.target.value })} />
          </div>
        )}
      </Modal>
      <ConfirmDialog open={!!removeId} danger busy={removing} title="删除批次" message="删除后无法恢复。已有档案的批次不能删除，请编辑并设为“已结束”。" onClose={() => { if (!removing) setRemoveId(null) }} onConfirm={async () => {
        if (removing) return
        setRemoving(true)
        try {
          await deleteBatch(removeId)
          setRemoveId(null)
          toast.success("批次已删除")
          req.reload().catch((e) => toast.error(`删除成功，但列表刷新失败：${e.message || "请重试"}`))
        } catch (e) {
          toast.error(e.message || "删除失败")
        } finally {
          setRemoving(false)
        }
      }} />
    </div>
  )
}
