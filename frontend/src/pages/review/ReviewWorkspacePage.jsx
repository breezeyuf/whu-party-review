import { useMemo, useState } from "react"
import { Link, useParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import MaterialViewer from "../../components/material/MaterialViewer"
import IssueList from "../../components/review/IssueList"
import IssueActions from "../../components/review/IssueActions"
import AddIssueModal from "../../components/review/AddIssueModal"
import ReportSummary from "../../components/review/ReportSummary"
import CompletenessTable from "../../components/review/CompletenessTable"
import ReviewDecisionPanel from "../../components/review/ReviewDecisionPanel"
import ReviewTrail from "../../components/review/ReviewTrail"
import TimelineView from "../../components/archive/TimelineView"
import NodeCorrectionModal from "../../components/archive/NodeCorrectionModal"
import RecheckSummary from "../../components/review/RecheckSummary"
import JobProgress from "../../components/common/JobProgress"
import { DemoBadge, StatusBadge } from "../../components/common/Badges"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { useJobPolling } from "../../hooks/useJobPolling"
import { getSubmission, reviewRecords, reviewSubmission, fileSubmission } from "../../api/submissions"
import { addIssue, listIssues } from "../../api/issues"
import { aiCheck, completeness, getReport, postHandover } from "../../api/reports"
import { correctNode, getTimeline } from "../../api/archives"
import { useToast } from "../../context/ToastContext"

const TABS = [
  ["issues", "问题清单"],
  ["timeline", "时间轴"],
  ["complete", "完整性"],
  ["report", "AI 报告"],
  ["trail", "审核记录"],
]

export default function ReviewWorkspacePage() {
  const { id } = useParams()
  const toast = useToast()
  const [aiBusy, setAiBusy] = useState(false)
  const subReq = useRequest(() => getSubmission(id), [id])
  const sub = subReq.data
  const issueReq = useRequest(() => listIssues(id), [id])
  const compReq = useRequest(() => completeness(id, { live: true }), [id])
  const trailReq = useRequest(() => reviewRecords(id), [id])
  const reportId = sub?.latest_report?.id
  const reportReq = useRequest(() => (reportId ? getReport(reportId) : null), [reportId], { immediate: !!reportId })
  const archiveId = sub?.archive?.id
  const timeReq = useRequest(() => (archiveId ? getTimeline(archiveId) : null), [archiveId], { immediate: !!archiveId })

  const [tab, setTab] = useState("issues")
  const [activeIssue, setActiveIssue] = useState(null)
  const [materialId, setMaterialId] = useState(null)
  const [page, setPage] = useState(1)
  const [adding, setAdding] = useState(false)
  const [correcting, setCorrecting] = useState(null)
  const [jobId, setJobId] = useState(null)

  const materials = sub?.materials || []
  const currentMat = materials.find((m) => m.id === (materialId || activeIssue?.location?.material_id || activeIssue?.material_id)) || materials[0]

  const highlights = useMemo(() => (issueReq.data?.items || []).map((issue) => ({
    id: issue.id,
    page_no: issue.location?.page_no,
    bbox: issue.location?.bbox,
    title: issue.title,
    material_id: issue.material_id || issue.location?.material_id,
  })).filter((h) => !currentMat || h.material_id === currentMat.id || !h.material_id), [issueReq.data, currentMat])

  const { job, error: jobError } = useJobPolling(jobId, { onDone: async () => {
    const results = await refreshAll()
    if (results.some((result) => result.status === "rejected")) toast.info("AI 审核已完成，但部分内容刷新失败；请手动刷新工作区")
  } })

  const selectIssue = (issue) => {
    setActiveIssue(issue)
    const mid = issue.material_id || issue.location?.material_id
    if (mid) setMaterialId(mid)
    if (issue.location?.page_no) setPage(issue.location.page_no)
  }

  const refreshAll = () => {
    return Promise.allSettled([subReq.reload(), issueReq.reload(), reportReq.reload(), trailReq.reload(), compReq.reload(), timeReq.reload()])
  }

  if (subReq.loading && !sub) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={subReq.reload} />
  if (!sub) return null

  return (
    <div>
      <PageHeader
        title={`${sub.archive?.real_name || ""} · ${sub.stage_name || ""}`}
        crumbs={[{ label: "审核待办", to: "/review/tasks" }, { label: "工作区" }]}
        extra={(
          <>
            <StatusBadge code={sub.status} />
            <DemoBadge show={sub.archive?.is_demo || sub.is_demo} />
            {sub.can?.ai_check && (
              <button type="button" className="btn btn-outline btn-sm" disabled={aiBusy} onClick={async () => {
                setAiBusy(true)
                try {
                  const res = await aiCheck(id, {})
                  setJobId(res.job_id)
                  toast.info("已发起 AI 审核")
                } catch (e) {
                  toast.error(e.message || "发起 AI 审核失败")
                } finally {
                  setAiBusy(false)
                }
              }}>{aiBusy ? "发起中…" : "AI 审核"}</button>
            )}
            {sub.can?.add_issue && <button type="button" className="btn btn-ghost btn-sm" onClick={() => setAdding(true)}>新增问题</button>}
            <Link className="btn btn-ghost btn-sm" to={`/archives/${sub.archive?.id}`}>档案</Link>
          </>
        )}
      >
        {sub.archive?.student_no} · {sub.archive?.branch_name} · 第 {sub.round_no} 轮
      </PageHeader>
      {jobId && <div className="mb-3"><JobProgress job={job} /></div>}
      {jobError && <div className="alert alert-warning mb-3 text-sm">暂时无法获取 AI 任务进度：{jobError.message || "请稍后刷新工作区"}</div>}
      <p className="mb-3 text-xs text-base-content/55">AI 结果用于辅助核查；请结合材料原文和审核规则作出人工决定。</p>
      <div className="grid gap-4 xl:grid-cols-2">
        <section className="surface-card p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-sm font-semibold">材料原文</h2>
            {currentMat && <span className="text-xs text-base-content/50">{currentMat.title || currentMat.type_name}</span>}
          </div>
          <div className="mb-2 flex flex-wrap gap-1 border-b border-base-200 pb-2">
            {materials.map((m) => (
              <button key={m.id} type="button" className={`btn btn-xs ${currentMat?.id === m.id ? "btn-primary" : "btn-ghost"}`} aria-pressed={currentMat?.id === m.id} title={m.title || m.type_name} onClick={() => { setMaterialId(m.id); setPage(1) }}>
                <span className="max-w-48 truncate">{m.title || m.type_name}</span>{m.open_issue_count ? <span className="badge badge-xs">{m.open_issue_count}</span> : ""}
              </button>
            ))}
          </div>
          {currentMat ? (
            <MaterialViewer
              materialId={currentMat.id}
              versionId={currentMat.current_version_id}
              page={page}
              onPage={setPage}
              highlights={highlights}
              activeId={activeIssue?.id}
            />
          ) : <p className="text-sm text-base-content/50">该提交包还没有材料。</p>}
        </section>
        <section>
          <div role="tablist" aria-label="审核信息面板" className="tabs tabs-bordered mb-3">
            {TABS.map(([k, label]) => (
              <button key={k} type="button" role="tab" aria-selected={tab === k} className={`tab ${tab === k ? "tab-active" : ""}`} onClick={() => setTab(k)}>
                {label}{k === "issues" && issueReq.data?.items?.length > 0 && <span className="badge badge-ghost badge-xs ml-1">{issueReq.data.items.length}</span>}
              </button>
            ))}
          </div>
          {tab === "issues" && (
            issueReq.error ? <ErrorState error={issueReq.error} onRetry={issueReq.reload} /> : issueReq.loading && !issueReq.data ? <Loading label="加载问题清单" /> : (
              <IssueList
                issues={issueReq.data?.items || []}
                activeId={activeIssue?.id}
                onSelect={selectIssue}
                renderActions={(issue) => sub.can?.add_issue ? <IssueActions issue={issue} onChanged={() => issueReq.reload().catch(() => toast.info("问题操作已完成，但列表刷新失败"))} /> : null}
              />
            )
          )}
          {tab === "timeline" && (
            timeReq.error ? <ErrorState error={timeReq.error} onRetry={timeReq.reload} /> : timeReq.loading && !timeReq.data ? <Loading label="加载时间节点" /> : (
              <TimelineView
                timeline={timeReq.data}
                onCorrect={sub.can?.edit_timeline ? setCorrecting : undefined}
                onLocate={(src) => { setMaterialId(src.material_id); setPage(src.page_no || 1); setTab("issues") }}
              />
            )
          )}
          {tab === "complete" && (compReq.error ? <ErrorState error={compReq.error} onRetry={compReq.reload} /> : compReq.loading && !compReq.data ? <Loading label="检查材料完整性" /> : <div className="surface-card p-3"><CompletenessTable data={compReq.data || sub.completeness} /></div>)}
          {tab === "report" && (
            <div className="space-y-3">
              {reportReq.error ? <ErrorState error={reportReq.error} onRetry={reportReq.reload} /> : reportReq.loading && !reportReq.data ? <Loading label="加载 AI 报告" /> : <>
                <div className="surface-card p-3"><ReportSummary report={reportReq.data} /></div>
                <RecheckSummary summary={reportReq.data?.recheck_summary} />
              </>}
            </div>
          )}
          {tab === "trail" && (trailReq.error ? <ErrorState error={trailReq.error} onRetry={trailReq.reload} /> : trailReq.loading && !trailReq.data ? <Loading label="加载审核记录" /> : <ReviewTrail records={trailReq.data || []} />)}
        </section>
      </div>
      <div className="mt-4">
        <ReviewDecisionPanel
          key={`${id}:${reportId}`}
          submission={sub}
          issues={issueReq.data?.items || []}
          onPass={async (body) => { await reviewSubmission(id, body); toast.success("已通过"); const results = await refreshAll(); if (results.some((result) => result.status === "rejected")) toast.info("审核已通过，但部分内容刷新失败；请刷新工作区") }}
          onReturn={async (body) => { await reviewSubmission(id, body); toast.success("已退回"); const results = await refreshAll(); if (results.some((result) => result.status === "rejected")) toast.info("已退回，但部分内容刷新失败；请刷新工作区") }}
          onFile={async (body) => { await fileSubmission(id, body); toast.success("已备案"); const results = await refreshAll(); if (results.some((result) => result.status === "rejected")) toast.info("已备案，但部分内容刷新失败；请刷新工作区") }}
          onHandover={async (body) => { await postHandover(reportId, body); toast.success("已接管"); const results = await refreshAll(); if (results.some((result) => result.status === "rejected")) toast.info("接管已完成，但部分内容刷新失败；请刷新工作区") }}
        />
      </div>
      <AddIssueModal
        open={adding}
        materials={materials}
        onClose={() => setAdding(false)}
        onCreate={async (body) => { await addIssue(id, body); toast.success("已新增"); await issueReq.reload().catch(() => toast.info("问题已新增，但列表刷新失败；请刷新工作区")) }}
      />
      {correcting && archiveId && (
        <NodeCorrectionModal
          node={correcting}
          onClose={() => setCorrecting(null)}
          onSave={(body) => correctNode(archiveId, correcting.code, body).then(async () => {
            toast.success("节点已校正")
            await timeReq.reload().catch(() => toast.info("节点已校正，但时间轴刷新失败；请刷新工作区"))
          })}
        />
      )}
    </div>
  )
}
