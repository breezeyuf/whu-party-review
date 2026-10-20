import { useEffect, useMemo, useRef, useState } from "react"
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
import ReviewJobStatus from "../../components/review/ReviewJobStatus"
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
  const [aiBusy, setAiBusy] = useState(false)
  const subReq = useRequest(() => getSubmission(id), [id, roleKey])
  const sub = subReq.data
  const issueReq = useRequest(() => loadAllReviewIssues((params) => listIssues(id, params)), [id, roleKey])
  const compReq = useRequest(() => completeness(id, { live: true }), [id, roleKey])
  const trailReq = useRequest(() => reviewRecords(id), [id, roleKey])
  const reportId = sub?.latest_report?.id
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
  const [correcting, setCorrecting] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [noticeId, setNoticeId] = useState(null)

  useEffect(() => {
    locateSequence.current += 1
    setActiveIssueId(null); setMaterialSelection(null); setPage(1)
    setJobId(null); setNoticeId(null); setLocationNote(""); setTimelineHighlight(null)
    setAdding(false); setCorrecting(null); setTab("issues")
    return () => { locateSequence.current += 1 }
  }, [id, roleKey])

  const materials = sub?.materials || []
  const issues = issueReq.data?.items || []
  const activeIssue = issues.find((issue) => sameId(issue.id, activeIssueId))
  const currentMat = materialSelection ? materials.find((m) => sameId(m.id, materialSelection.materialId)) : materials[0]
  const currentVersion = materialSelection?.versionId || currentMat?.current_version_id
  const highlights = useMemo(() => [
    ...issueHighlights(issueReq.data?.items || [], currentMat, currentVersion),
    ...(timelineHighlight && sameId(timelineHighlight.materialId, currentMat?.id) && sameId(timelineHighlight.versionId, currentVersion) ? [timelineHighlight] : []),
  ], [issueReq.data, currentMat, currentVersion, timelineHighlight])
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

  return (
    <div className="review-workspace">
      <PageHeader
        title={`${sub.archive?.real_name || ""} · ${sub.stage_name || ""}`}
        crumbs={[{ label: "审核待办", to: "/review/tasks" }, { label: "工作区" }]}
        extra={(
          <>
            <StatusBadge code={sub.status} />
            <DemoBadge show={sub.archive?.is_demo || sub.is_demo} />
            <details className="service-more-actions"><summary>更多操作</summary><div>
            {sub.can?.ai_check && !needsAiCheck && (
              <button type="button" className="btn btn-outline btn-sm" disabled={aiBusy || ["QUEUED", "RUNNING"].includes(sub.ai_status)} onClick={startAiCheck}>{aiBusy ? "发起中…" : ["QUEUED", "RUNNING"].includes(sub.ai_status) ? "AI 检查中…" : sub.ai_status === "FAILED" ? "重新 AI 审核" : "AI 审核"}</button>
            )}
            {sub.can?.add_issue && <button type="button" className="btn btn-ghost btn-sm" onClick={() => setAdding(true)}>新增问题</button>}
            <Link className="btn btn-ghost btn-sm" to={`/archives/${sub.archive?.id}`}>查看档案</Link>
            <button type="button" className="btn btn-ghost btn-sm" disabled={subReq.loading} onClick={refreshAll}>刷新</button>
            </div></details>
          </>
        )}
      >
        {sub.archive?.student_no} · {sub.archive?.branch_name} · 第 {sub.round_no} 轮
      </PageHeader>
      {trackedJobId && <div className="mb-3"><ReviewJobStatus jobId={trackedJobId} onDone={refreshAll} onRetry={refreshAll} /></div>}
      {reportBlockReason(sub) && <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-warning" role="status"><p>{reportBlockReason(sub)}</p>{needsAiCheck && <button type="button" className="btn btn-outline btn-sm" disabled={aiBusy} onClick={startAiCheck}>{aiBusy ? "发起中…" : "开始自动核对"}</button>}</div>}
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
            <span>{sameId(currentVersion, currentMat.current_version_id) ? `当前版本 v${currentMat.version_no || "—"}` : `问题原文版本 #${currentVersion}（历史版本）`}</span>
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
          {tab === "issues" && issueReq.error && <ErrorState error={issueReq.error} onRetry={() => issueReq.reload().catch(() => {})} />}
          {tab === "issues" && issueReq.loading && !issueReq.data && <Loading label="加载完整问题清单" />}
          {tab === "issues" && issueReq.data && (
            <IssueList
              issues={issueReq.data?.items || []}
              activeId={activeIssue?.id}
              onSelect={selectIssue}
              renderActions={(issue) => sub.can?.add_issue ? <IssueActions issue={issue} disabled={issueReq.loading || subReq.loading} onChanged={refreshAll} /> : null}
            />
          )}
          {tab === "timeline" && timeReq.error && <ErrorState error={timeReq.error} onRetry={() => timeReq.reload().catch(() => {})} />}
          {tab === "timeline" && timeReq.loading && <Loading label="加载时间轴" />}
          {tab === "timeline" && !timeReq.loading && !timeReq.error && (
            <TimelineView
              timeline={timeReq.data}
              onCorrect={sub.can?.edit_timeline ? setCorrecting : undefined}
              onLocate={locateTimeline}
            />
          )}
          {tab === "complete" && (compReq.error ? <ErrorState error={compReq.error} onRetry={() => compReq.reload().catch(() => {})} /> : compReq.loading ? <Loading label="核对材料完整性" /> : <div className="surface-card p-3"><CompletenessTable data={compReq.data} /></div>)}
          {tab === "report" && (
            <div className="space-y-3">
              {reportReq.error ? <ErrorState error={reportReq.error} onRetry={() => reportReq.reload().catch(() => {})} /> : reportReq.loading ? <Loading label="加载审核报告" /> : <div className="surface-card p-3"><ReportSummary report={reportReq.data} /></div>}
              <RecheckSummary summary={reportReq.data?.recheck_summary} />
            </div>
          )}
          {tab === "trail" && (trailReq.error ? <ErrorState error={trailReq.error} onRetry={() => trailReq.reload().catch(() => {})} /> : trailReq.loading ? <Loading label="加载审核记录" /> : <ReviewTrail records={trailReq.data || []} />)}
        </div></section>
      <section id="review-decision" className="review-decision">
        <ReviewDecisionPanel
          key={`${id}:${reportId}:${sub.status}:${roleKey}`}
          submission={sub}
          issues={issueReq.data?.items || []}
          issuesReady={!!issueReq.data && !issueReq.loading && !issueReq.error && !subReq.loading && !subReq.error}
          onPass={async (body) => { await reviewSubmission(id, body); toast.success("已通过并流转至下一层级"); await refreshAll() }}
          onReturn={async (body) => { const result = await reviewSubmission(id, body); setNoticeId(result.notice_id); toast.success("已退回并发送整改通知"); await refreshAll() }}
          onFile={async (body) => { await fileSubmission(id, body); toast.success("已备案，档案阶段已更新"); await refreshAll() }}
          onHandover={async (body) => { await postHandover(reportId, body); toast.success("已提交人工结论，请继续完成审核决定"); await refreshAll() }}
        />
      </section>
      </div></div>
      {adding && <AddIssueModal
        open={adding}
        materials={materials}
        onClose={() => setAdding(false)}
        onCreate={async (body) => { await addIssue(id, body); toast.success("已新增人工问题并确认"); await refreshAll() }}
      />}
      {correcting && archiveId && (
        <NodeCorrectionModal
          node={correcting}
          onClose={() => setCorrecting(null)}
          onSave={async (body) => { await correctNode(archiveId, correcting.code, body); await refreshAll(); toast.success("节点已校正，请重新运行 AI 审核更新报告") }}
        />
      )}
    </div>
  )
}
