import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import NoticePreview from "../../components/notice/NoticePreview"
import { StatusBadge } from "../../components/common/Badges"
import { Modal } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { getNotice, listNotices, sendNotice } from "../../api/notices"
import { completionNotices } from "../../api/reports"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

export default function NoticesPage() {
  const toast = useToast()
  const [sp] = useSearchParams()
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => listNotices(query), [JSON.stringify(query)])
  const [current, setCurrent] = useState(null)
  const [open, setOpen] = useState(false)
  const [ids, setIds] = useState("")
  const [deadline, setDeadline] = useState("")

  useEffect(() => {
    const nid = sp.get("notice")
    if (nid) getNotice(nid).then(setCurrent).catch(() => {})
  }, [sp])

  const openOne = async (row) => setCurrent(await getNotice(row.id))

  const generate = async () => {
    const submission_ids = ids.split(/[,，\s]+/).map((x) => Number(x)).filter(Boolean)
    if (!submission_ids.length) { toast.error("请填写提交包 ID"); return }
    try {
      const res = await completionNotices({ submission_ids, deadline: deadline || undefined, send: true })
      toast.success(`生成 ${res.created?.length || 0} 条，跳过 ${res.skipped?.length || 0} 条`)
      setOpen(false)
      req.reload()
    } catch (e) {
      toast.error(e.message || "生成失败")
    }
  }

  const doSend = async (notice) => {
    try {
      await sendNotice(notice.id)
      toast.success("已发送")
      setCurrent(await getNotice(notice.id))
      req.reload()
    } catch (e) {
      toast.error(e.message || "发送失败")
    }
  }

  return (
    <div>
      <PageHeader title="通知与补全" extra={<button type="button" className="btn btn-primary btn-sm" onClick={() => setOpen(true)}>批量补全提示</button>} />
      <FilterBar
        values={query}
        onChange={setQuery}
        fields={[
          { key: "notice_type", label: "类型", type: "select", options: [{ code: "COMPLETION", name: "补全提示" }, { code: "RECTIFICATION", name: "整改通知" }] },
          { key: "status", label: "状态", type: "select", options: [{ code: "DRAFT", name: "草稿" }, { code: "SENT", name: "已发送" }] },
          { key: "submission_id", label: "提交包 ID" },
        ]}
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="surface-card p-2">
          <DataTable
            loading={req.loading}
            rows={req.data?.items || []}
            columns={[
              { key: "title", title: "标题", render: (r) => <button type="button" className="link text-left text-xs" onClick={() => openOne(r)}>{r.title}</button> },
              { key: "who", title: "学生", render: (r) => <span className="text-xs">{r.student_name}<br />{r.stage_name}</span> },
              { key: "st", title: "状态", render: (r) => <StatusBadge code={r.status} map={{ DRAFT: "草稿", SENT: "已发送" }} /> },
              { key: "dl", title: "截止", render: (r) => fmtDate(r.deadline) },
            ]}
          />
          <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />
        </div>
        <div>
          <NoticePreview notice={current} />
          {current?.status === "DRAFT" && (
            <button type="button" className="btn btn-primary btn-sm mt-3" onClick={() => doSend(current)}>发送</button>
          )}
        </div>
      </div>
      <Modal open={open} title="生成材料补全提示" onClose={() => setOpen(false)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setOpen(false)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={generate}>生成并推送</button>
        </>
      }>
        <label className="form-control">
          <span className="label-text text-xs">提交包 ID，逗号分隔</span>
          <input className="input input-bordered input-sm" value={ids} onChange={(e) => setIds(e.target.value)} />
        </label>
        <label className="form-control mt-2">
          <span className="label-text text-xs">截止日期</span>
          <input type="date" className="input input-bordered input-sm" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
        </label>
      </Modal>
    </div>
  )
}
