import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import StageProgress from "../../components/archive/StageProgress"
import TimelineView from "../../components/archive/TimelineView"
import ReviewTrail from "../../components/review/ReviewTrail"
import { Loading, ErrorState } from "../../components/common/States"
import { StatusBadge } from "../../components/common/Badges"
import { useRequest } from "../../hooks/useRequest"
import { getHistory, getTimeline, myArchive } from "../../api/archives"

export default function MyProgressPage() {
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const id = archive?.id
  const timelineReq = useRequest(() => (id ? getTimeline(id) : null), [id], { immediate: !!id })
  const historyReq = useRequest(() => (id ? getHistory(id) : []), [id], { immediate: !!id })

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={archiveReq.reload} />

  const sub = archive?.current_submission
  const nextAction = sub?.next_action || (sub?.status === "RETURNED"
    ? "请处理整改问题后重新提交"
    : sub?.status && !["DRAFT"].includes(sub.status)
      ? "材料已提交，请等待审核"
      : "请按当前阶段材料清单补充材料并完成自查")
  const visibleNodeCount = (timelineReq.data?.nodes || []).filter((node) => node.code !== "T01" && !/出生日期|出生年月/.test(node.name || "")).length
  return (
    <div>
      <PageHeader title="我的发展进度" extra={sub?.id && <Link className="btn btn-primary btn-sm" to={`/my/self-check/${sub.id}`}>{["DRAFT", "RETURNED"].includes(sub.status) ? "AI 自查与提交" : "自查报告"}</Link>}>
        {archive?.current_submission?.next_action || archive?.next_action}
      </PageHeader>
      <div className="surface-card mb-5 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-base-200 px-4 py-3 sm:px-5">
          <div>
            <p className="text-xs text-base-content/55">当前培养阶段</p>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-sm font-semibold">
              <span>{archive?.stage_name || `阶段 ${archive?.current_stage || ""}`}</span>
              <StatusBadge code={sub?.status || archive?.status} />
            </div>
          </div>
          <span className="text-xs text-base-content/50">发展流程共 {timelineReq.data?.stages?.length || 0} 个阶段</span>
        </div>
        <div className="overflow-x-auto px-3 py-4 sm:px-5">
          <StageProgress current={archive?.current_stage} stages={timelineReq.data?.stages || []} submissionBase="/my/self-check" />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-5">
        <section className="surface-card min-w-0 p-4 sm:col-span-3 sm:p-5">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-2 border-b border-base-200 pb-3">
            <div>
              <h2 className="text-base font-semibold">时间节点</h2>
              <p className="mt-1 text-xs text-base-content/55">仅展示与党员发展流程相关的关键时间</p>
            </div>
            {visibleNodeCount > 0 && <span className="text-xs text-base-content/50">{visibleNodeCount} 个已识别节点</span>}
          </div>
          {timelineReq.loading && !timelineReq.data ? <Loading /> : timelineReq.error ? <ErrorState error={timelineReq.error} onRetry={() => timelineReq.reload().catch(() => {})} /> : <TimelineView timeline={timelineReq.data} hidePersonalInfo hideSources compact />}
        </section>
        <section className="surface-card min-w-0 p-4 sm:col-span-2 sm:p-5">
          <h2 className="mb-3 border-b border-base-200 pb-3 text-base font-semibold">发展历史</h2>
          {historyReq.loading ? <Loading /> : historyReq.error ? <ErrorState error={historyReq.error} onRetry={() => historyReq.reload().catch(() => {})} /> : <ReviewTrail records={Array.isArray(historyReq.data) ? historyReq.data : []} />}
        </section>
      </div>
    </div>
  )
}
