import { useEffect, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import NoticePreview from "../../components/notice/NoticePreview"
import { StatusBadge } from "../../components/common/Badges"
import { Modal } from "../../components/common/Modal"
import { ErrorState, Loading } from "../../components/common/States"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { getNotice, listNotices, sendNotice } from "../../api/notices"
import { completionNotices } from "../../api/reports"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

const isPositiveIntegerId = (value) => /^\d+$/.test(value) && Number.isSafeInteger(Number(value)) && Number(value) > 0

export default function NoticesPage() {
  const toast = useToast()
  const [sp] = useSearchParams()
  const { query, setQuery, setPage } = usePagination()
  const querySubmissionId = String(query.submission_id ?? "")
  const querySubmissionIdValid = !querySubmissionId || isPositiveIntegerId(querySubmissionId)
  const requestQuery = querySubmissionIdValid
    ? query
    : Object.fromEntries(Object.entries(query).filter(([key]) => key !== "submission_id"))
  const req = useRequest(() => listNotices(requestQuery), [JSON.stringify(requestQuery)])
  const [current, setCurrent] = useState(null)
  // 单条通知的读取状态：失败时在预览区提示并可重试
  const [noticeState, setNoticeState] = useState({ id: null, loading: false, error: null })
  const sequence = useRef(0)
  const [open, setOpen] = useState(false)
  const [ids, setIds] = useState("")
  const [submissionIdDraft, setSubmissionIdDraft] = useState(querySubmissionId)
  const [deadline, setDeadline] = useState("")
  const [generating, setGenerating] = useState(false)
  const [sendingId, setSendingId] = useState(null)
  const submissionIdInvalid = submissionIdDraft !== "" && !isPositiveIntegerId(submissionIdDraft)

  useEffect(() => {
    setSubmissionIdDraft(querySubmissionId)
  }, [querySubmissionId])

  const updateFilters = (patch) => {
    if (Object.hasOwn(patch, "submission_id")) {
      const value = String(patch.submission_id ?? "")
      setSubmissionIdDraft(value)
      if (value && !isPositiveIntegerId(value)) return
    }
    setQuery(patch)
  }

  const openOne = async (noticeId) => {
    const request = ++sequence.current
    setNoticeState({ id: noticeId, loading: true, error: null })
    try {
      const notice = await getNotice(noticeId)
      if (request !== sequence.current) return
      setCurrent(notice)
      setNoticeState({ id: noticeId, loading: false, error: null })
    } catch (error) {
      if (request === sequence.current) setNoticeState({ id: noticeId, loading: false, error })
    }
  }

  useEffect(() => {
    const nid = sp.get("notice")
    if (nid) openOne(nid)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sp])

  const generate = async () => {
    if (generating) return
    const rawIds = ids.split(/[,，\s]+/).map((x) => x.trim()).filter(Boolean)
    const submission_ids = [...new Set(rawIds.map(Number))]
    if (rawIds.some((value) => !/^\d+$/.test(value) || Number(value) < 1)) {
      toast.error("提交包 ID 只能填写正整数，并用逗号或空格分隔")
      return
    }
    if (!submission_ids.length) { toast.error("请填写提交包 ID"); return }
    setGenerating(true)
    try {
      const res = await completionNotices({ submission_ids, deadline: deadline || undefined, send: true })
      toast.success(`生成 ${res.created?.length || 0} 条，跳过 ${res.skipped?.length || 0} 条`)
      setOpen(false)
      setIds("")
      setDeadline("")
      req.reload().catch(() => {})
    } catch (e) {
      toast.error(e.message || "生成失败")
    } finally {
      setGenerating(false)
    }
  }

  const doSend = async (notice) => {
    if (sendingId != null) return
    setSendingId(notice.id)
    try {
      await sendNotice(notice.id)
    } catch (e) {
      toast.error(e.message || "发送失败")
      return
    } finally {
      setSendingId(null)
    }
    toast.success("已发送")
    openOne(notice.id)
    req.reload().catch(() => {})
  }

  return (
    <div>
      <PageHeader title="通知与补件" extra={<button type="button" className="btn btn-primary btn-sm" onClick={() => setOpen(true)}>批量补全提示</button>} />
      <FilterBar
        values={{ ...query, submission_id: submissionIdDraft }}
        onChange={updateFilters}
        fields={[
          { key: "notice_type", label: "类型", type: "select", options: [{ code: "COMPLETION", name: "补全提示" }, { code: "RECTIFICATION", name: "整改通知" }] },
          { key: "status", label: "状态", type: "select", options: [{ code: "DRAFT", name: "草稿" }, { code: "SENT", name: "已发送" }] },
          { key: "submission_id", label: "提交包 ID" },
        ]}
      />
      {submissionIdInvalid && <p className="mt-2 text-sm text-error" role="alert">提交包 ID 只能填写正整数；当前列表仍按上次有效条件显示。</p>}
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="surface-card p-2">
          <DataTable
            loading={req.loading}
            error={req.error}
            onRetry={req.reload}
            rows={req.data?.items || []}
            empty={query.notice_type || query.status || query.submission_id ? "没有符合条件的通知" : "还没有通知"}
            columns={[
              { key: "title", title: "标题", render: (r) => <button type="button" className="link text-left text-xs" onClick={() => openOne(r.id)}>{r.title}</button> },
              { key: "who", title: "学生", render: (r) => <span className="text-xs">{r.student_name}<br />{r.stage_name}</span> },
              { key: "st", title: "状态", render: (r) => <StatusBadge code={r.status} map={{ DRAFT: "草稿", SENT: "已发送" }} /> },
              { key: "dl", title: "截止", render: (r) => fmtDate(r.deadline) },
            ]}
          />
          {!req.error && <Pager page={req.data?.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })} />}
        </div>
        <div>
          {noticeState.loading && <Loading label="通知" />}
          {noticeState.error && <ErrorState title="通知加载失败" error={noticeState.error} onRetry={() => openOne(noticeState.id)} />}
          {!noticeState.loading && !noticeState.error && <>
            <NoticePreview notice={current} />
            {current?.status === "DRAFT" && (
              <button type="button" className="btn btn-primary btn-sm mt-3" disabled={sendingId != null} onClick={() => doSend(current)}>{sendingId === current.id ? "发送中…" : "发送"}</button>
            )}
          </>}
        </div>
      </div>
      <Modal open={open} title="生成材料补全提示" onClose={() => setOpen(false)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" disabled={generating} onClick={() => setOpen(false)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={generating} onClick={generate}>{generating ? "生成中…" : "生成并推送"}</button>
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
