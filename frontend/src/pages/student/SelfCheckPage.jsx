import { useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { ArrowRight, FileText, ListChecks, RefreshCw, Send } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import ReportSummary from "../../components/review/ReportSummary"
import CompletenessTable from "../../components/review/CompletenessTable"
import IssueList from "../../components/review/IssueList"
import IssueResponseForm from "../../components/student/IssueResponseForm"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { aiCheck, completeness, getReport } from "../../api/reports"
import { getSubmission, submitSubmission } from "../../api/submissions"
import { listIssues } from "../../api/issues"
import { useToast } from "../../context/ToastContext"
import StudentTaskProgress from "../../utils/student/StudentTaskProgress"
import { isAiPending, issueMaterialId, refreshStudentRequests, studentSubmitReason } from "../../utils/studentWorkflow"
import { useStudentMaterials } from "../../utils/student/useStudentMaterials"

export default function SelfCheckPage() {
  const { submissionId } = useParams()
  const toast = useToast()
  const subReq = useRequest(() => getSubmission(submissionId), [submissionId])
  const compReq = useRequest(() => completeness(submissionId, { live: true }), [submissionId])
  const issueReq = useRequest(() => listIssues(submissionId, { active: true }), [submissionId])
  const latestId = subReq.data?.latest_report?.id
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedReportId = /^[1-9]\d*$/.test(searchParams.get("report") || "") ? Number(searchParams.get("report")) : null
  const reportId = requestedReportId || latestId
  // 档案历史里的报告事件：按编号只读查看，提交与整改仍按当前状态判断
  const viewingHistoryReport = !!requestedReportId && requestedReportId !== latestId
  const backToLatestReport = () => {
    const next = new URLSearchParams(searchParams)
    next.delete("report")
    setSearchParams(next, { replace: true })
  }
  const reportReq = useRequest(() => (reportId ? getReport(reportId) : null), [reportId], { immediate: !!reportId })
  const [startedTask, setStartedTask] = useState(null)
  const [finishedJobId, setFinishedJobId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [starting, setStarting] = useState(false)
  const [confirmSubmit, setConfirmSubmit] = useState(false)
  const [tab, setTab] = useState("overview")
  const [error, setError] = useState("")
  const [replyWork, setReplyWork] = useState({})
  const actionLock = useRef(false)
  const sub = subReq.data
  const jobId = (isAiPending(sub) ? sub.ai_job_id : null) || (startedTask && startedTask.submissionId === submissionId ? startedTask.id : null)
  const taskPending = !!jobId && String(jobId) !== String(finishedJobId)
  const issues = issueReq.data?.items || []
  const materialsReq = useStudentMaterials(sub?.archive?.id, sub?.stage_code, () => refreshStudentRequests(subReq, issueReq, compReq, ...(latestId ? [reportReq] : [])))
  const replyBusy = Object.values(replyWork).some(Boolean)
  const materialBusy = materialsReq.loading || !materialsReq.data || !!materialsReq.error || materialsReq.pending > 0
  const submitReason = materialBusy ? (materialsReq.pending ? "材料正在解析，请完成后再提交。" : "正在核对材料状态，请稍候；加载失败时请重试。") : studentSubmitReason(sub, issues, { ready: !!issueReq.data && !issueReq.loading && !issueReq.error && !subReq.loading, taskPending: taskPending || replyBusy })
  const canCheck = !!sub?.can?.self_check && !taskPending && !replyBusy && !materialBusy && !isAiPending(sub)
  const refresh = () => refreshStudentRequests(subReq, issueReq, compReq, ...(latestId ? [reportReq] : []))

  const start = async () => {
    if (actionLock.current || !canCheck) return
    actionLock.current = true
    setError("")
    setStarting(true)
    try {
      const res = await aiCheck(submissionId, {})
      if (!res?.job_id) throw new Error("服务未返回检查任务编号，请刷新后重试")
      setFinishedJobId(null)
      setStartedTask({ submissionId, id: res.job_id })
      toast.info("已发起自查")
      refresh()
    } catch (e) {
      setError(e.message || "发起自查失败")
    } finally {
      setStarting(false)
      actionLock.current = false
    }
  }

  const submit = async () => {
    if (actionLock.current || submitReason) return
    actionLock.current = true
    setBusy(true)
    setError("")
    try {
      const res = await submitSubmission(submissionId, {})
      if (res?.submission) subReq.setData(res.submission)
      if (res?.recheck_job_id) {
        setFinishedJobId(null)
        setStartedTask({ submissionId, id: res.recheck_job_id })
      }
      toast.success(res?.recheck_job_id ? "已重新提交，系统正在复核" : "已提交审核")
      refresh()
    } catch (e) {
      setError(e.message || "无法提交")
      refresh()
    } finally {
      setBusy(false)
      actionLock.current = false
    }
  }

  if (subReq.loading && !sub) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={() => subReq.reload().catch(() => {})} />

  return (
    <div>
      <PageHeader title="自查与提交" crumbs={[{ label: "我的材料", to: "/my/materials" }, { label: "自查与提交" }]}
        extra={<>
          <button type="button" className="btn btn-outline btn-sm" disabled={starting || busy || !canCheck} onClick={start}>{starting ? "发起中…" : taskPending || isAiPending(sub) ? "自查进行中…" : "发起自查"}</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={busy || starting || !!submitReason} onClick={submit}>{busy ? "提交中…" : sub?.status === "RETURNED" ? "重新提交" : "提交审核"}</button>
        </>}>
        {sub?.stage_name} · AI 结论作为参考，提交前请处理待回复问题。
      </PageHeader>
      {viewingHistoryReport && <div className="surface-card mb-3 flex flex-wrap items-center gap-3 p-3 text-sm" role="status">
        <span className="badge badge-warning badge-sm">历史报告</span>
        <span>正在查看报告 #{reportId} 的当时快照，仅供复核；提交状态与待回复问题仍以最新情况为准。</span>
        <button type="button" className="btn btn-ghost btn-xs" onClick={backToLatestReport}>返回最新报告</button>
      </div>}
      {jobId && <div className="mb-4"><StudentTaskProgress jobId={jobId} onDone={(job) => { setFinishedJobId(job.id); refresh() }} onRestart={() => { setFinishedJobId(null); refresh() }} /></div>}
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {materialsReq.error && <ErrorState error={materialsReq.error} onRetry={() => materialsReq.reload().catch(() => {})} />}
      {submitReason && <div className="alert alert-warning mb-3 text-sm">{submitReason}</div>}
      {sub?.status === "RETURNED" && <p className="mb-3 text-sm">退回整改后可直接重提，由系统自动复核。<Link className="link" to="/my/rectification">前往整改中心</Link></p>}
      <details className="service-details mb-5" open={!!compReq.error || !!reportReq.error || (compReq.data && !compReq.data.is_complete) ? true : undefined}>
      <summary>查看自查报告与材料清单</summary>
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">报告摘要</h2>
          {reportReq.loading && !reportReq.data ? <Loading /> : reportReq.error ? <ErrorState error={reportReq.error} onRetry={() => reportReq.reload().catch(() => {})} /> : <ReportSummary report={viewingHistoryReport ? reportReq.data : (reportReq.data ? { ...reportReq.data, is_stale: sub?.latest_report?.is_stale || reportReq.data.is_stale } : sub?.latest_report)} />}
          <Link className="btn btn-ghost btn-xs mt-3" to="/my/rectification">去整改中心</Link>
        </section>
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">材料完整性</h2>
          {compReq.loading && !compReq.data ? <Loading /> : compReq.error ? <ErrorState error={compReq.error} onRetry={() => compReq.reload().catch(() => {})} /> : <CompletenessTable data={compReq.data} />}
        </section>
      </div>
      </details>
      <section className="mt-4">
        <h2 className="mb-2 text-sm font-medium">问题与修改建议</h2>
        {issueReq.loading && !issueReq.data ? <Loading /> : issueReq.error ? <ErrorState error={issueReq.error} onRetry={() => issueReq.reload().catch(() => {})} /> : <IssueList issues={issues}
          readonlyNote="逐条整改或填写情况说明；材料解析失败不代表检查通过。"
          renderActions={(issue) => issueMaterialId(issue) && <Link className="btn btn-ghost btn-xs" to={`/materials/${issueMaterialId(issue)}?issue_id=${issue.id}`}>查看问题材料</Link>}
          renderFooter={(issue) => sub?.can?.submit && !taskPending && !isAiPending(sub) && <IssueResponseForm compact issue={issue} onDone={() => { refresh(); materialsReq.reload().catch(() => {}) }} onBusyChange={(value) => setReplyWork((previous) => previous[issue.id] === value ? previous : { ...previous, [issue.id]: value })} />}
        />}
      </section>
    </div>
  )
}
