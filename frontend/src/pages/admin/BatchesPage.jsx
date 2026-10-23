import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable from "../../components/common/DataTable"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { createBatch, deleteBatch, listBatches, updateBatch } from "../../api/batches"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

const EMPTY = { name: "", year: new Date().getFullYear(), term: "全年", stage_codes: "1,2,3,4,5", start_date: "", end_date: "", branch_deadline: "", college_deadline: "", org_deadline: "", description: "" }

const TERM_NAME = { FULL_YEAR: "全年", H1: "上半年", H2: "下半年", 全年: "全年" }
const BATCH_STATUS = { PLANNED: "筹备中", ACTIVE: "进行中", CLOSED: "已结束", ARCHIVED: "已归档" }

export default function BatchesPage() {
  const toast = useToast()
  const req = useRequest(() => listBatches({ page_size: 50 }), [])
  const [edit, setEdit] = useState(null)
  const [removeId, setRemoveId] = useState(null)
  const rows = req.data?.items || []

  const save = async () => {
    const body = {
      ...edit,
      year: Number(edit.year),
      stage_codes: String(edit.stage_codes || "").split(/[,，]/).map((s) => Number(s.trim())).filter(Boolean),
    }
    try {
      if (edit.id) await updateBatch(edit.id, body)
      else await createBatch(body)
      toast.success("已保存")
      setEdit(null)
      req.reload()
    } catch (e) {
      toast.error(e.message || "保存失败")
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
              <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => setRemoveId(r.id)}>删除</button>
            </>
          ) },
        ]} />
      </div>
      <Modal open={!!edit} wide title={edit?.id ? "编辑批次" : "新建批次"} onClose={() => setEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={save}>保存</button>
        </>
      }>
        {edit && (
          <div className="grid gap-2 sm:grid-cols-2">
            <input className="input input-bordered input-sm sm:col-span-2" placeholder="名称" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
            <input className="input input-bordered input-sm" type="number" placeholder="年度" value={edit.year} onChange={(e) => setEdit({ ...edit, year: e.target.value })} />
            <input className="input input-bordered input-sm" placeholder="学期" value={edit.term || ""} onChange={(e) => setEdit({ ...edit, term: e.target.value })} />
            <input className="input input-bordered input-sm" type="date" value={edit.start_date || ""} onChange={(e) => setEdit({ ...edit, start_date: e.target.value })} />
            <input className="input input-bordered input-sm" type="date" value={edit.end_date || ""} onChange={(e) => setEdit({ ...edit, end_date: e.target.value })} />
            <input className="input input-bordered input-sm" type="date" value={String(edit.branch_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, branch_deadline: e.target.value })} />
            <input className="input input-bordered input-sm" type="date" value={String(edit.college_deadline || "").slice(0, 10)} onChange={(e) => setEdit({ ...edit, college_deadline: e.target.value })} />
            <input className="input input-bordered input-sm sm:col-span-2" placeholder="阶段编码 1,2,3,4,5" value={edit.stage_codes} onChange={(e) => setEdit({ ...edit, stage_codes: e.target.value })} />
            <textarea className="textarea textarea-bordered text-sm sm:col-span-2" rows={2} placeholder="说明" value={edit.description || ""} onChange={(e) => setEdit({ ...edit, description: e.target.value })} />
          </div>
        )}
      </Modal>
      <ConfirmDialog open={!!removeId} danger title="删除批次" message="已有档案时后端会拒绝，请改为关闭。" onClose={() => setRemoveId(null)} onConfirm={async () => {
        try {
          await deleteBatch(removeId)
          setRemoveId(null)
          req.reload()
        } catch (e) {
          toast.error(e.message || "删除失败")
        }
      }} />
    </div>
  )
}
