import { Suspense, useEffect, useMemo, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import MaterialViewer from "../../components/material/MaterialViewer"
import IssueList from "../../components/review/IssueList"
import IssueActions from "../../components/review/IssueActions"
import ReportSummary from "../../components/review/ReportSummary"
import CompletenessTable from "../../components/review/CompletenessTable"
import ReviewDecisionPanel from "../../components/review/ReviewDecisionPanel"
import ReviewTrail from "../../components/review/ReviewTrail"
import TimelineView from "../../components/archive/TimelineView"
import RecheckSummary from "../../components/review/RecheckSummary"
import { DemoBadge, StatusBadge } from "../../components/common/Badges"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { getSubmission, reviewRecords, reviewSubmission, fileSubmission } from "../../api/submissions"
import { addIssue, listIssues } from "../../api/issues"
import { aiCheck, completeness, getReport, postHandover } from "../../api/reports"
import { correctNode, getTimeline } from "../../api/archives"
import { listVersions } from "../../api/materials"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { issueHighlights, issueLocation, loadAllReviewIssues, reportBlockReason, sameId } from "../../utils/review"
import { ModalLoading } from "../../components/common/Modal"
import { lazyWithRetry, whenIdle } from "../../utils/lazyLoad"
import { reportMaterials, reportTimeline } from "../../utils/reportSnapshot"

// 只在打开时才用到的弹窗不进页面首屏；有权使用时在页面空闲时提前下载，打开时不再等待
const AddIssueModal = lazyWithRetry(() => import("../../components/review/AddIssueModal"))
const NodeCorrectionModal = lazyWithRetry(() => import("../../components/archive/NodeCorrectionModal"))
// AI 检查进行中或失败时才显示任务进度
const ReviewJobStatus = lazyWithRetry(() => import("../../components/review/ReviewJobStatus"))

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
  const { activeRole } = useAuth()
  const roleKey = `${activeRole?.role}:${activeRole?.org_id}`
  const [searchParams, setSearchParams] = useSearchParams()
  const [aiBusy, setAiBusy] = useState(false)
  const subReq = useRequest(() => getSubmission(id), [id, roleKey])
  const sub = subReq.data
  const issueReq = useRequest(() => loadAllReviewIssues((params) => listIssues(id, params)), [id, roleKey])
  const compReq = useRequest(() => completeness(id, { live: true }), [id, roleKey])
  const trailReq = useRequest(() => reviewRecords(id), [id, roleKey])
  const latestReportId = sub?.latest_report?.id
  const requestedReportId = /^[1-9]\d*$/.test(searchParams.get("report") || "") ? Number(searchParams.get("report")) : null
  const reportId = requestedReportId || latestReportId
  // 历史事件里的报告编号：只读查看当时快照，审核决定仍然针对最新报告
  const viewingHistoryReport = !!requestedReportId && requestedReportId !== latestReportId
  const backToLatestReport = () => {
    const next = new URLSearchParams(searchParams)
    next.delete("report")
    setSearchParams(next, { replace: true })
  }
  const reportReq = useRequest(() => (reportId ? getReport(reportId) : null), [id, reportId, roleKey], { immediate: !!reportId })
  const archiveId = sub?.archive?.id
  const timeReq = useRequest(() => (archiveId ? getTimeline(archiveId) : null), [id, archiveId, roleKey], { immediate: !!archiveId })

  const [tab, setTab] = useState("issues")
  const [activeIssueId, setActiveIssueId] = useState(null)
  const [materialSelection, setMaterialSelection] = useState(null)
  const [locationNote, setLocationNote] = useState("")
  const [timelineHighlight, setTimelineHighlight] = useState(null)
  const locateSequence = useRef(0)
  const [page, setPage] = useState(1)
  const [adding, setAdding] = useState(false)
  const [newIssueLocation, setNewIssueLocation] = useState(null)
  const [correcting, setCorrecting] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [noticeId, setNoticeId] = useState(null)

  useEffect(() => {
    locateSequence.current += 1
    setActiveIssueId(null); setMaterialSelection(null); setPage(1)
    setJobId(null); setNoticeId(null); setLocationNote(""); setTimelineHighlight(null)
    setAdding(false); setNewIssueLocation(null); setCorrecting(null); setTab("issues")
    return () => { locateSequence.current += 1 }
  }, [id, roleKey, reportId])

  const canAddIssue = !!sub?.can?.add_issue
  const canEditTimeline = !!sub?.can?.edit_timeline
  useEffect(() => (canAddIssue ? whenIdle(() => AddIssueModal.preload().catch(() => {}), 0) : undefined), [canAddIssue])
  useEffect(() => (canEditTimeline ? whenIdle(() => NodeCorrectionModal.preload().catch(() => {}), 0) : undefined), [canEditTimeline])

  const issues = issueReq.data?.items || []
  // 历史报告模式用报告自带快照：问题、完整性、材料版本都按当时那一刻展示，不混入当前状态
  const historyReport = viewingHistoryReport && sameId(reportReq.data?.id, reportId) ? reportReq.data : null
  const historyIssues = Object.values(historyReport?.issues_by_category || {}).flat()
  const snapshotMode = viewingHistoryReport
  const materials = snapshotMode ? reportMaterials(historyReport, sub?.materials) : sub?.materials || []
  const shownTimeline = snapshotMode ? reportTimeline(historyReport) : timeReq.data
  const shownIssues = snapshotMode ? historyIssues : issues
  const shownCompleteness = snapshotMode ? historyReport?.completeness : compReq.data
  // 报告必须属于当前提交包，否则会把别的问题挂在这条提交包下
  const reportMismatch = !!historyReport && !sameId(historyReport.submission_id, id)
  const activeIssue = shownIssues.find((issue) => sameId(issue.id, activeIssueId))
  const currentMat = materialSelection ? materials.find((m) => sameId(m.id, materialSelection.materialId)) : materials[0]
  const currentVersion = materialSelection?.versionId || currentMat?.current_version_id
  const highlights = useMemo(() => [
    ...issueHighlights(shownIssues, currentMat, currentVersion),
    ...(timelineHighlight && sameId(timelineHighlight.materialId, currentMat?.id) && sameId(timelineHighlight.versionId, currentVersion) ? [timelineHighlight] : []),
  ], [shownIssues, currentMat, currentVersion, timelineHighlight])
  const trackedJobId = jobId || (["QUEUED", "RUNNING", "FAILED"].includes(sub?.ai_status) ? sub?.ai_job_id : null)

  const selectIssue = (issue) => {
    locateSequence.current += 1
    setActiveIssueId(issue.id)
    setTimelineHighlight(null)
    const target = issueLocation(issue)
    const material = materials.find((m) => sameId(m.id, target.materialId))
    const resolved = issueLocation(issue, material)
    setMaterialSelection(resolved.materialId ? resolved : null)
    setPage(resolved.page)
    setLocationNote(!resolved.materialId ? "此问题未关联具体材料，可结合问题说明与时间轴核实。" : !material ? "问题所关联的材料已不在当前提交包中，请查看问题说明。" : !issue.location?.page_no ? "此问题未提供精确页码，已打开对应材料版本。" : "")
  }

  const refreshAll = () => Promise.allSettled([subReq.reload(), issueReq.reload(), reportReq.reload(), trailReq.reload(), compReq.reload(), timeReq.reload()])

  const needsAiCheck = !!sub?.can?.ai_check && !!reportBlockReason(sub) && !["QUEUED", "RUNNING"].includes(sub?.ai_status)
  const startAiCheck = async () => {
    if (aiBusy || ["QUEUED", "RUNNING"].includes(sub?.ai_status)) return
    setAiBusy(true)
    try {
      const result = await aiCheck(id, {})
      if (!result?.job_id) throw new Error("服务未返回检查任务编号，请刷新后重试")
      subReq.setData((current) => ({ ...current, ai_status: "QUEUED", ai_job_id: result.job_id }))
      setJobId(result.job_id)
      toast.info("已发起 AI 审核")
    } catch (error) { toast.error(error.message || "发起 AI 审核失败") }
    finally { setAiBusy(false) }
  }

  const locateTimeline = async (source) => {
    const sequence = ++locateSequence.current
    try {
      const material = materials.find((m) => sameId(m.id, source.material_id))
      if (!material) throw new Error("时间轴来源材料已不在当前提交包中")
      let versionId = source.material_version_id || source.version_id || material.current_version_id
      if (!source.material_version_id && !source.version_id && source.version_no != null && !sameId(source.version_no, material.version_no)) {
        const versions = await listVersions(material.id)
        if (sequence !== locateSequence.current) return
        const version = versions.find((v) => sameId(v.version_no, source.version_no))
        if (!version) throw new Error("未找到时间轴来源版本，请刷新后重试")
        versionId = version.id
      }
      setActiveIssueId(null)
      setMaterialSelection({ materialId: material.id, versionId })
      setTimelineHighlight({ id: "timeline-source", materialId: material.id, versionId, page_no: source.page_no, bbox: source.bbox, title: source.raw_text || "时间轴来源" })
      setLocationNote(source.page_no ? "" : "该时间轴来源没有页码，已打开对应材料版本。")
      setPage(source.page_no || 1)
    } catch (error) { if (sequence === locateSequence.current) toast.error(error.message || "定位失败") }
  }

  if (subReq.loading && !sub) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={() => subReq.reload().catch(() => {})} />
  if (!sub) return null
  if (snapshotMode && !historyReport) return <div><button type="button" className="btn btn-ghost" onClick={backToLatestReport}>返回最新报告</button>{reportReq.error ? <ErrorState error={reportReq.error} onRetry={() => reportReq.reload().catch(() => {})} /> : <Loading label="历史报告" />}</div>
  if (reportMismatch) return (
    <div className="review-workspace">
      <PageHeader title="报告与提交包不匹配" extra={<Link className="btn btn-outline btn-sm" to={`/review/submissions/${historyReport.submission_id}?report=${historyReport.id}`}>打开所属提交包</Link>} />
      <div className="surface-card p-4 text-sm" role="alert">
        报告 #{historyReport.id} 属于提交包 #{historyReport.submission_id}，不是当前 #{id}。
      </div>
    </div>
  )

  return (
    <div className="review-workspace">
      <PageHeader
        title={`${sub.archive?.real_name || ""} · ${sub.stage_name || ""}`}
        extra={(
          <>
            <StatusBadge code={sub.status} />
            <DemoBadge show={sub.archive?.is_demo || sub.is_demo} />
            <details className="service-more-actions"><summary>更多操作</summary><div>
            {!snapshotMode && sub.can?.ai_check && !needsAiCheck && (
              <button type="button" className="btn btn-outline btn-sm" disabled={aiBusy || ["QUEUED", "RUNNING"].includes(sub.ai_status)} onClick={startAiCheck}>{aiBusy ? "发起中…" : ["QUEUED", "RUNNING"].includes(sub.ai_status) ? "AI 检查中…" : sub.ai_status === "FAILED" ? "重新 AI 审核" : "AI 审核"}</button>
            )}
            {!snapshotMode && sub.can?.add_issue && <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setNewIssueLocation(null); setAdding(true) }}>新增问题</button>}
            <Link className="btn btn-ghost btn-sm" to={`/archives/${sub.archive?.id}`}>查看档案</Link>
            <button type="button" className="btn btn-ghost btn-sm" disabled={subReq.loading} onClick={refreshAll}>刷新</button>
            </div></details>
          </>
        )}
      >
        {sub.archive?.student_no} · {sub.archive?.branch_name} · 第 {sub.round_no} 轮
      </PageHeader>
      {trackedJobId && <div className="mb-3"><Suspense fallback={<p className="text-xs text-base-content/60" role="status">正在加载任务状态…</p>}><ReviewJobStatus jobId={trackedJobId} onDone={refreshAll} onRetry={refreshAll} /></Suspense></div>}
      {viewingHistoryReport && <div className="surface-card mb-3 flex flex-wrap items-center gap-3 p-3 text-sm" role="status">
        <span className="badge badge-warning badge-sm">历史报告</span>
        <span>报告 #{reportId} 快照：问题、完整性与结论取自该次报告；审核决定仍以最新报告为准。</span>
        <button type="button" className="btn btn-ghost btn-xs" onClick={backToLatestReport}>返回最新报告</button>
      </div>}
      {!snapshotMode && reportBlockReason(sub) && <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-warning" role="status"><p>{reportBlockReason(sub)}</p>{needsAiCheck && <button type="button" className="btn btn-outline btn-sm" disabled={aiBusy} onClick={startAiCheck}>{aiBusy ? "发起中…" : "开始自动核对"}</button>}</div>}
      {noticeId && <div className="surface-card mb-3 p-3 text-sm">已生成并发送整改通知。<Link className="link ml-2" to={`/notices?notice=${noticeId}`}>查看整改通知</Link></div>}
      <nav className="review-stage-links" aria-label="审核步骤"><a href="#review-materials"><span>1</span>核对材料</a><a href="#review-issues"><span>2</span>处理问题</a><a href="#review-decision"><span>3</span>填写结论</a></nav>
      <div className="review-grid">
        <section id="review-materials" className="surface-card p-4 review-preview">
          <h2 className="mb-3 text-base font-semibold">材料原文</h2>
          {materials.length > 0 && <select aria-label="选择预览材料" className="select select-bordered select-sm review-material-select" value={currentMat?.id || ""} onChange={(event) => { const material = materials.find((item) => sameId(item.id, event.target.value)); if (!material) return; locateSequence.current += 1; setMaterialSelection({ materialId: material.id, versionId: material.current_version_id }); setActiveIssueId(null); setTimelineHighlight(null); setLocationNote(""); setPage(1) }}>
            {materials.map((material) => <option key={material.id} value={material.id}>{material.title || material.type_name}{material.open_issue_count ? ` · ${material.open_issue_count} 个问题` : ""}</option>)}
          </select>}
          {locationNote && <p className="mb-2 text-xs text-warning" role="status">{locationNote}</p>}
          {currentMat && <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-base-content/60">
            <span>{snapshotMode ? `报告原文版本 #${currentVersion}` : sameId(currentVersion, currentMat.current_version_id) ? `当前版本 v${currentMat.version_no || "—"}` : `问题原文版本 #${currentVersion}（历史版本）`}</span>
            {!sameId(currentVersion, currentMat.current_version_id) && <button type="button" className="btn btn-ghost btn-xs" onClick={() => { setMaterialSelection({ materialId: currentMat.id, versionId: currentMat.current_version_id }); setActiveIssueId(null); setTimelineHighlight(null); setPage(1) }}>查看当前版本</button>}
            <Link className="link" to={`/materials/${currentMat.id}?version_id=${currentVersion || ""}&page=${page}${activeIssue ? `&issue_id=${activeIssue.id}` : ""}`}>材料详情</Link>
          </div>}
          <div className="preview-scroll">
          {currentMat ? (
            <MaterialViewer
              key={`${currentMat.id}:${currentVersion}`}
              materialId={currentMat.id}
              versionId={currentVersion}
              page={page}
              onPage={setPage}
              highlights={highlights}
              activeId={activeIssue?.id || timelineHighlight?.id}
              onSelectRegion={!snapshotMode && sub.can?.add_issue && sameId(currentVersion, currentMat.current_version_id) ? (location) => { setNewIssueLocation(location); setAdding(true) } : undefined}
            />
          ) : <p className="text-sm text-base-content/50">{materials.length ? "请选择当前提交包中的材料。" : "该提交包还没有材料。"}</p>}
        </div></section>
        <div>
        <section id="review-issues">
          <div className="review-reference-toolbar">
            <div className="review-switch" aria-label="工作区内容"><button type="button" aria-pressed={tab === "issues"} onClick={() => setTab("issues")}>待核对问题</button><button type="button" aria-pressed={tab !== "issues"} onClick={() => setTab("report")}>参考资料</button></div>
            {tab !== "issues" && <select aria-label="查看参考资料" className="select select-bordered select-sm" value={tab} onChange={(event) => setTab(event.target.value)}>{TABS.filter(([key]) => key !== "issues").map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>}
          </div>
          <div className="review-issues-pane">
          {tab === "issues" && issueReq.error && !snapshotMode && <ErrorState error={issueReq.error} onRetry={() => issueReq.reload().catch(() => {})} />}
          {tab === "issues" && issueReq.loading && !issueReq.data && !snapshotMode && <Loading label="完整问题清单" />}
          {tab === "issues" && (snapshotMode || issueReq.data) && (
            <IssueList
              issues={shownIssues}
              activeId={activeIssue?.id}
              onSelect={selectIssue}
              renderActions={(issue) => !snapshotMode && sub.can?.add_issue ? <IssueActions issue={issue} disabled={issueReq.loading || subReq.loading} onChanged={refreshAll} /> : null}
            />
          )}
          {tab === "timeline" && !snapshotMode && timeReq.error && <ErrorState error={timeReq.error} onRetry={() => timeReq.reload().catch(() => {})} />}
          {tab === "timeline" && !snapshotMode && timeReq.loading && <Loading label="时间轴" />}
          {tab === "timeline" && (snapshotMode || (!timeReq.loading && !timeReq.error)) && (
            <TimelineView
              allowLockedCorrection={activeRole?.role === "ORG_ADMIN"}
              timeline={shownTimeline}
              onCorrect={!snapshotMode && sub.can?.edit_timeline ? setCorrecting : undefined}
              onLocate={locateTimeline}
            />
          )}
          {tab === "complete" && (snapshotMode
            ? <div className="surface-card p-3"><CompletenessTable data={shownCompleteness} /></div>
            : compReq.error ? <ErrorState error={compReq.error} onRetry={() => compReq.reload().catch(() => {})} /> : compReq.loading ? <Loading label="材料完整性" /> : <div className="surface-card p-3"><CompletenessTable data={compReq.data} /></div>)}
          {tab === "report" && (
            <div className="space-y-3">
              {reportReq.error ? <ErrorState error={reportReq.error} onRetry={() => reportReq.reload().catch(() => {})} /> : reportReq.loading ? <Loading label="审核报告" /> : <div className="surface-card p-3"><ReportSummary report={reportReq.data} /></div>}
              <RecheckSummary summary={reportReq.data?.recheck_summary} />
            </div>
          )}
          {tab === "trail" && (trailReq.error ? <ErrorState error={trailReq.error} onRetry={() => trailReq.reload().catch(() => {})} /> : trailReq.loading ? <Loading label="审核记录" /> : <ReviewTrail records={trailReq.data || []} />)}
        </div></section>
      <section id="review-decision" className="review-decision">
        {snapshotMode ? <div className="surface-card p-4 text-sm" role="status">
          <p className="mb-2 font-medium">历史报告模式：审核决定只针对最新报告。</p>
          <button type="button" className="btn btn-outline btn-sm mt-3" onClick={backToLatestReport}>返回最新报告</button>
        </div> : (
        <ReviewDecisionPanel
          key={`${id}:${reportId}:${sub.status}:${roleKey}`}
          submission={sub}
          issues={issueReq.data?.items || []}
          issuesReady={!!issueReq.data && !issueReq.loading && !issueReq.error && !subReq.loading && !subReq.error}
          onPass={async (body) => { await reviewSubmission(id, body); toast.success("已通过并流转至下一层级"); await refreshAll() }}
          onReturn={async (body) => { const result = await reviewSubmission(id, body); setNoticeId(result.notice_id); toast.success("已退回并发送整改通知"); await refreshAll() }}
          onFile={async (body) => { await fileSubmission(id, body); toast.success("已备案，档案阶段已更新"); await refreshAll() }}
          onHandover={async (body) => { await postHandover(latestReportId, body); toast.success("已提交人工结论，请继续完成审核决定"); await refreshAll() }}
        />
        )}
      </section>
      </div></div>
      {adding && <Suspense fallback={<ModalLoading />}><AddIssueModal
        open={adding}
        materials={materials}
        initialLocation={newIssueLocation}
        onClose={() => { setAdding(false); setNewIssueLocation(null) }}
        onCreate={async (body) => { await addIssue(id, body); toast.success("已新增人工问题并确认"); await refreshAll() }}
      /></Suspense>}
      {correcting && archiveId && (
        <Suspense fallback={<ModalLoading />}><NodeCorrectionModal
          node={correcting}
          onClose={() => setCorrecting(null)}
          onSave={async (body) => { await correctNode(archiveId, correcting.code, body); await refreshAll(); toast.success("节点已校正，请重新运行 AI 审核更新报告") }}
        /></Suspense>
      )}
    </div>
  )
}
