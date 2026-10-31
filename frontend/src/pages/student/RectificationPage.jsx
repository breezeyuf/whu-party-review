import { useRef, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import StudentFlowGuide from "../../components/student/StudentFlowGuide"
import PageHeader from "../../components/layout/PageHeader"
import IssueList from "../../components/review/IssueList"
import IssueResponseForm from "../../components/student/IssueResponseForm"
import RecheckSummary from "../../components/review/RecheckSummary"
import NoticePreview from "../../components/notice/NoticePreview"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { myArchive } from "../../api/archives"
import { listIssues } from "../../api/issues"
import { getNotice, listNotices } from "../../api/notices"
import { getReport } from "../../api/reports"
import { getSubmission, submitSubmission } from "../../api/submissions"
import { useToast } from "../../context/ToastContext"
import StudentTaskProgress from "../../utils/student/StudentTaskProgress"
import { pendingStudentReplies, isAiPending, issueMaterialId, refreshStudentRequests, studentSubmitReason } from "../../utils/studentWorkflow"
import { useStudentMaterials } from "../../utils/student/useStudentMaterials"

export default function RectificationPage() {
  const toast = useToast()
  const [searchParams, setSearchParams] = useSearchParams()
  const [issueView, setIssueView] = useState("pending")
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const subId = archive?.current_submission?.id
  const subReq = useRequest(() => (subId ? getSubmission(subId) : null), [subId], { immediate: !!subId })
  const issueReq = useRequest(() => (subId ? listIssues(subId) : { items: [] }), [subId], { immediate: !!subId })
  const noticeReq = useRequest(() => listNotices({ submission_id: subId, notice_type: "RECTIFICATION", page_size: 20 }), [subId], { immediate: !!subId })
  const [notice, setNotice] = useState(null)
  const [noticeLoading, setNoticeLoading] = useState(false)
  const [noticeError, setNoticeError] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [startedTask, setStartedTask] = useState(null)
  const [finishedJobId, setFinishedJobId] = useState(null)
  const [replyWork, setReplyWork] = useState({})
  const replyDrafts = useRef(new Map())
  const requestLock = useRef(false)
  const noticeSequence = useRef(0)
  const sub = subReq.data
  const reportId = sub?.latest_report?.id
  const reportReq = useRequest(() => (reportId ? getReport(reportId) : null), [reportId], { immediate: !!reportId })
  const jobId = (isAiPending(sub) ? sub.ai_job_id : null) || (startedTask && startedTask.submissionId === subId ? startedTask.id : null)
  const taskPending = !!jobId && String(jobId) !== String(finishedJobId)
  const replyBusy = Object.values(replyWork).some(Boolean)
  const materialsReq = useStudentMaterials(archive?.id, sub?.stage_code, () => refreshStudentRequests(subReq, issueReq, ...(reportId ? [reportReq] : [])))
  const refresh = () => refreshStudentRequests(subReq, issueReq, noticeReq, ...(reportId ? [reportReq] : []))
  const materialBusy = materialsReq.loading || !materialsReq.data || !!materialsReq.error || materialsReq.pending > 0
  const submitReason = materialBusy ? (materialsReq.pending ? "材料正在解析，请完成后再重新提交。" : "正在核对材料状态，请稍候；加载失败时请重试。") : studentSubmitReason(sub, issueReq.data?.items || [], { ready: !!issueReq.data && !issueReq.loading && !issueReq.error && !subReq.loading, taskPending: taskPending || replyBusy })

  const openNotice = async (id) => {
    const sequence = ++noticeSequence.current
    setNotice(null)
    setNoticeError("")
    setNoticeLoading(true)
    try {
      const data = await getNotice(id)
      if (sequence === noticeSequence.current) setNotice(data)
    } catch (e) {
      if (sequence === noticeSequence.current) setNoticeError(e.message || "通知加载失败")
    } finally {
      if (sequence === noticeSequence.current) setNoticeLoading(false)
    }
  }

  const resubmit = async () => {
    if (requestLock.current || submitReason || sub?.status !== "RETURNED") return
    requestLock.current = true
    setBusy(true)
    setError("")
    try {
      const res = await submitSubmission(subId, {})
      if (res?.submission) subReq.setData(res.submission)
      if (res?.recheck_job_id) {
        setFinishedJobId(null)
        setStartedTask({ submissionId: subId, id: res.recheck_job_id })
      }
      toast.success("已重新提交，系统正在自动复核")
      refresh()
    } catch (e) {
      setError(e.message || "还不能重新提交")
      refresh()
    } finally {
      setBusy(false)
      requestLock.current = false
    }
  }

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={() => archiveReq.reload().catch(() => {})} />
  if (!subId) return <div><PageHeader title="整改中心" /><p className="text-sm text-base-content/60">当前没有待整改的提交。</p></div>
  if (subReq.loading && !sub) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={() => subReq.reload().catch(() => {})} />
  const returned = sub?.status === "RETURNED"
  const allIssues = issueReq.data?.items || []
  const requiredReplies = pendingStudentReplies(sub, allIssues)
  const focusIssue = searchParams.get("issue_id")
  const onlyPending = returned && issueView === "pending" && !focusIssue
  const shownIssues = onlyPending ? requiredReplies : allIssues
  const canReply = !!sub?.can?.submit && ["DRAFT", "RETURNED"].includes(sub?.status) && !taskPending && !isAiPending(sub)

  return (
    <div>
      <PageHeader title="整改中心" extra={returned && <button type="button" className="btn btn-primary btn-sm" disabled={busy || !!submitReason} onClick={resubmit}>{busy ? "重新提交中…" : "重新提交"}</button>}>
        {returned ? "逐条回复已确认的问题。全部处理后重新提交，系统会自动复核。" : "查看整改回复与复核记录；当前办理状态以页面提示为准。"}
      </PageHeader>
      <StudentFlowGuide submission={sub} issues={allIssues} groups={materialsReq.data || []} ready={!!issueReq.data && !!materialsReq.data && !issueReq.error && !materialsReq.error && !subReq.loading} taskPending={taskPending || replyBusy} source="rectification" blockedReason={returned ? (replyBusy ? "正在保存整改或解析新版本，请等待完成。" : submitReason) : ""}/>
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {materialsReq.error && <ErrorState error={materialsReq.error} onRetry={() => materialsReq.reload().catch(() => {})} />}
      {sub?.status === "DRAFT" && <div className="text-sm mb-3">{sub?.status === "DRAFT" ? <>当前为草稿，请完成自查后从<Link className="link" to={`/my/self-check/${subId}`}>自查页提交审核</Link>。</> : "材料已进入审核，当前可查看整改回复与复核结果。"}</div>}
      {jobId && <div className="mb-4"><StudentTaskProgress jobId={jobId} onDone={(job) => { setFinishedJobId(job.id); refresh() }} onRestart={() => { setFinishedJobId(null); refresh() }} /></div>}
      {reportReq.error && <ErrorState error={reportReq.error} onRetry={() => reportReq.reload().catch(() => {})} />}
      {reportReq.loading && !reportReq.data && <Loading label="复核报告" />}
      {reportReq.data?.recheck_summary && <div className="mb-4"><RecheckSummary summary={reportReq.data.recheck_summary} /></div>}
      <div className="grid gap-4 lg:grid-cols-5">
        <section className="lg:col-span-3">
          {returned && <div className="mb-3 flex flex-wrap items-center gap-2" aria-label="整改问题范围">
            <button type="button" className={`btn btn-sm ${onlyPending ? "btn-primary" : "btn-ghost"}`} disabled={replyBusy} onClick={() => { setIssueView("pending"); if (focusIssue) { const next = new URLSearchParams(searchParams); next.delete("issue_id"); setSearchParams(next, { replace: true }) } }}>待我回复（{requiredReplies.length}）</button>
            <button type="button" className={`btn btn-sm ${!onlyPending ? "btn-primary" : "btn-ghost"}`} disabled={replyBusy} onClick={() => setIssueView("all")}>全部问题（{allIssues.length}）</button>
          </div>}
          {onlyPending && !requiredReplies.length && !issueReq.loading && !issueReq.error && <p className="surface-card mb-3 p-3 text-sm">待回复问题已处理。可查看全部问题与已保存回复，再重新提交。</p>}
          {issueReq.loading && !issueReq.data ? <Loading /> : issueReq.error ? <ErrorState error={issueReq.error} onRetry={() => issueReq.reload().catch(() => {})} /> : <IssueList
            key={subId} filtersDisabled={replyBusy} issues={shownIssues} activeId={focusIssue}
            renderActions={(issue) => issueMaterialId(issue) && <Link className="btn btn-ghost btn-xs" to={`/materials/${issueMaterialId(issue)}?issue_id=${issue.id}&from=rectification`}>查看问题材料</Link>}
            renderFooter={(issue) => canReply && issue.is_active !== false && issue.review_status !== "REJECTED" ? <IssueResponseForm compact issue={issue} drafts={replyDrafts.current} draftKey={`${subId}:${issue.id}`} onDone={() => { refresh(); materialsReq.reload().catch(() => {}) }} onBusyChange={(value) => setReplyWork((previous) => previous[issue.id] === value ? previous : { ...previous, [issue.id]: value })} /> : null}
          />}
        </section>
        <aside className="lg:col-span-2 space-y-3">
          <h2 className="text-sm font-medium">整改通知</h2>
          {noticeReq.loading && !noticeReq.data ? <Loading /> : noticeReq.error ? <ErrorState error={noticeReq.error} onRetry={() => noticeReq.reload().catch(() => {})} /> : <>
            {!(noticeReq.data?.items || []).length && <p className="text-sm text-base-content/60">暂无整改通知。</p>}
            <ul className="space-y-2">{(noticeReq.data?.items || []).map((n) => <li key={n.id}><button type="button" className="btn btn-ghost btn-sm h-auto w-full justify-start py-2 text-left" onClick={() => openNotice(n.id)}><span><span className="block">{n.title}</span><span className="text-xs text-base-content/50">{n.item_count} 条 · {n.status}</span></span></button></li>)}</ul>
          </>}
          {noticeLoading && <Loading label="通知" />}
          {noticeError && <div className="alert alert-error text-sm">{noticeError}</div>}
          <NoticePreview notice={notice} />
        </aside>
      </div>
    </div>
  )
}
