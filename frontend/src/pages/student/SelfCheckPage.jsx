import { useState } from "react"
import { Link, useParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import ReportSummary from "../../components/review/ReportSummary"
import CompletenessTable from "../../components/review/CompletenessTable"
import IssueList from "../../components/review/IssueList"
import JobProgress from "../../components/common/JobProgress"
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
  const [error, setError] = useState("")

  const { job } = useJobPolling(jobId, {
    onDone: () => {
      subReq.reload()
      issueReq.reload()
      reportList.reload()
      compReq.reload()
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

  const submit = async () => {
    setBusy(true)
    setError("")
    try {
      await submitSubmission(submissionId, {})
      toast.success("已提交")
      subReq.reload()
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
          <>
            <button type="button" className="btn btn-outline btn-sm" disabled={starting} onClick={start}>{starting ? "发起中…" : "发起自查"}</button>
            <button type="button" className="btn btn-primary btn-sm" disabled={busy || !canSubmit} onClick={submit}>提交审核</button>
          </>
        )}
      >
        {subReq.data?.stage_name} · 阻断问题未处理时不能提交
      </PageHeader>
      {jobId && <div className="mb-4"><JobProgress job={job} /></div>}
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {!canSubmit && pendingBlock > 0 && (
        <div className="alert alert-warning mb-3 text-sm">还有 {pendingBlock} 条阻断问题未回复。请到整改中心逐条处理，或在问题下填写情况说明。</div>
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">报告摘要</h2>
          <ReportSummary report={reportReq.data || (subReq.data?.latest_report ? { ...subReq.data.latest_report, summary: subReq.data.latest_report.summary } : null)} />
          <Link className="btn btn-ghost btn-xs mt-3" to="/my/rectification">去整改中心</Link>
        </section>
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">材料完整性</h2>
          <CompletenessTable data={compReq.data} />
        </section>
      </div>
      <section className="mt-4">
        <h2 className="mb-2 text-sm font-medium">问题与修改建议</h2>
        <IssueList issues={issues} readonlyNote="自查阶段可看到全部问题。提交前请处理阻断项。" />
      </section>
    </div>
  )
}
