import { useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowRight, FileText, ListChecks, RefreshCw, Send } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import ReportSummary from "../../components/review/ReportSummary"
import CompletenessTable from "../../components/review/CompletenessTable"
import IssueList from "../../components/review/IssueList"
import JobProgress from "../../components/common/JobProgress"
import { ConfirmDialog } from "../../components/common/Modal"
import { StatusBadge } from "../../components/common/Badges"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { useJobPolling } from "../../hooks/useJobPolling"
import { aiCheck, completeness, getReport, listReports } from "../../api/reports"
import { getSubmission, submitSubmission } from "../../api/submissions"
import { listIssues } from "../../api/issues"
import { useToast } from "../../context/ToastContext"

export default function SelfCheckPage() {
  const { submissionId } = useParams()
  const toast = useToast()
  const subReq = useRequest(() => getSubmission(submissionId), [submissionId])
  const compReq = useRequest(() => completeness(submissionId, { live: true }), [submissionId])
  const issueReq = useRequest(() => listIssues(submissionId, { active: true }), [submissionId])
  const reportList = useRequest(() => listReports(submissionId), [submissionId])
  const latestId = subReq.data?.latest_report?.id || reportList.data?.[0]?.id
  const reportReq = useRequest(() => (latestId ? getReport(latestId) : null), [latestId], { immediate: !!latestId })
  const [jobId, setJobId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [starting, setStarting] = useState(false)
  const [confirmSubmit, setConfirmSubmit] = useState(false)
  const [tab, setTab] = useState("overview")
  const [error, setError] = useState("")

  const { job, error: jobError } = useJobPolling(jobId, {
    onDone: () => {
      Promise.allSettled([subReq.reload(), issueReq.reload(), reportList.reload(), compReq.reload()]).then((results) => {
        if (results.some((result) => result.status === "rejected")) {
          toast.info("自查已完成，但部分结果未刷新；请稍后重试")
        }
      })
    },
  })

  const start = async () => {
    setError("")
    setStarting(true)
    try {
      const res = await aiCheck(submissionId, {})
      setJobId(res.job_id)
      toast.info("已发起自查")
    } catch (e) {
      setError(e.message || "发起自查失败")
    } finally {
      setStarting(false)
    }
  }

  const issues = issueReq.data?.items || []
  const pendingBlock = (issueReq.data?.counts?.pending_block) || issues.filter((i) => i.severity === "BLOCK" && i.resolution !== "RESOLVED" && !i.response_type).length
  const canSubmit = subReq.data?.can?.submit
  const canStartCheck = subReq.data?.can?.ai_check
  const jobRunning = job?.status === "QUEUED" || job?.status === "RUNNING"
  const submitHint = pendingBlock > 0
    ? `还有 ${pendingBlock} 条阻断问题未处理，请先到整改中心逐条回复。`
    : subReq.data?.latest_report?.is_stale
      ? "材料或时间信息在上次自查后有变化，请重新发起 AI 自查。"
      : subReq.data?.ai_status !== "DONE"
        ? "请先完成 AI 自查，完成后才能提交审核。"
        : "当前提交状态暂不可提交，请检查是否已进入审核流程。"

  const submit = async () => {
    setBusy(true)
    setError("")
    try {
      await submitSubmission(submissionId, {})
      toast.success("已提交")
      setConfirmSubmit(false)
      try {
        await subReq.reload()
      } catch {
        toast.info("提交已成功，但状态刷新失败；请重新加载页面查看")
      }
    } catch (e) {
      setError(e.message || "无法提交")
    } finally {
      setBusy(false)
    }
  }

  if (subReq.loading && !subReq.data) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={subReq.reload} />

  return (
    <div>
      <PageHeader
        title="AI 自查"
        crumbs={[{ label: "我的材料", to: "/my/materials" }, { label: "自查" }]}
        extra={(
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn btn-outline btn-sm" disabled={starting || jobRunning || !canStartCheck} onClick={start}>
              <RefreshCw size={15} strokeWidth={1.8} />
              {starting ? "发起中…" : jobRunning ? "自查进行中…" : "发起自查"}
            </button>
            <button type="button" className="btn btn-primary btn-sm" disabled={busy || !canSubmit} onClick={() => setConfirmSubmit(true)}>
              <Send size={15} strokeWidth={1.8} />提交审核
            </button>
          </div>
        )}
      >
        <span className="mr-2">{subReq.data?.stage_name}</span>
        <StatusBadge code={subReq.data?.status} />
        {subReq.data?.latest_report?.is_stale && <span className="badge badge-warning badge-sm ml-2">自查结果已过期</span>}
      </PageHeader>
      {jobId && <div className="mb-4"><JobProgress job={job} /></div>}
      {jobError && <div className="alert alert-warning mb-3 text-sm">暂时无法刷新自查任务状态，系统会继续尝试；也可稍后重新打开本页查看。</div>}
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {!canSubmit && <div className="alert alert-warning mb-3 text-sm">{submitHint}</div>}
      <div role="tablist" aria-label="自查内容" className="tabs tabs-bordered mb-3">
        <button type="button" role="tab" aria-selected={tab === "overview"} className={`tab gap-2 ${tab === "overview" ? "tab-active" : ""}`} onClick={() => setTab("overview")}>
          <FileText size={15} strokeWidth={1.8} />检查概览
        </button>
        <button type="button" role="tab" aria-selected={tab === "issues"} className={`tab gap-2 ${tab === "issues" ? "tab-active" : ""}`} onClick={() => setTab("issues")}>
          <ListChecks size={15} strokeWidth={1.8} />问题与建议
          {issues.length > 0 && <span className="badge badge-ghost badge-xs">{issues.length}</span>}
        </button>
      </div>
      {tab === "overview" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <section className="surface-card p-4">
            <h2 className="mb-3 text-sm font-medium">AI 检查摘要</h2>
            {reportReq.error ? <div className="alert alert-error text-sm">报告详情加载失败：{reportReq.error.message}<button type="button" className="btn btn-xs" onClick={reportReq.reload}>重试</button></div> : (
              <ReportSummary report={reportReq.data || (subReq.data?.latest_report ? { ...subReq.data.latest_report, summary: subReq.data.latest_report.summary } : null)} />
            )}
            <Link className="btn btn-ghost btn-sm mt-3" to="/my/rectification">查看整改中心<ArrowRight size={15} strokeWidth={1.8} /></Link>
          </section>
          <section className="surface-card p-4">
            <h2 className="mb-3 text-sm font-medium">材料完整性</h2>
            {compReq.error ? <div className="alert alert-error text-sm">完整性检查加载失败：{compReq.error.message}<button type="button" className="btn btn-xs" onClick={compReq.reload}>重试</button></div> : (
              compReq.loading && !compReq.data ? <div className="py-6 text-center text-sm text-base-content/50">正在检查材料完整性…</div> : <CompletenessTable data={compReq.data} />
            )}
          </section>
        </div>
      ) : (
        <section>
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-sm font-medium">问题与修改建议</h2>
            <Link className="btn btn-ghost btn-sm" to="/my/rectification">去整改中心<ArrowRight size={15} strokeWidth={1.8} /></Link>
          </div>
          {issueReq.error ? <div className="alert alert-error text-sm">问题列表加载失败：{issueReq.error.message}<button type="button" className="btn btn-xs" onClick={issueReq.reload}>重试</button></div> : (
            <IssueList issues={issues} readonlyNote="自查阶段可查看问题与建议。提交前请处理阻断项。" />
          )}
        </section>
      )}
      <ConfirmDialog
        open={confirmSubmit}
        title="确认提交审核？"
        message="提交后材料将进入审核流程并暂时锁定，不能继续修改。请确认材料已齐全且自查结果为最新。"
        confirmText="确认提交"
        busy={busy}
        onClose={() => { if (!busy) setConfirmSubmit(false) }}
        onConfirm={submit}
      />
    </div>
  )
}
