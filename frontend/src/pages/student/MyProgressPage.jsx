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
  return (
    <div>
      <PageHeader title="我的发展进度" extra={sub?.id && <Link className="btn btn-primary btn-sm" to={`/my/self-check/${sub.id}`}>去自查</Link>}>
        {archive?.current_submission?.next_action || archive?.next_action}
      </PageHeader>
      <div className="surface-card mb-4 overflow-x-auto p-4">
        <div className="mb-3 flex items-center gap-2 text-sm">
          <span>{archive?.stage_name || `阶段 ${archive?.current_stage || ""}`}</span>
          <StatusBadge code={sub?.status || archive?.status} />
        </div>
        <StageProgress current={archive?.current_stage} stages={timelineReq.data?.stages || []} submissionBase="/my/self-check" />
      </div>
      <div className="grid gap-4 lg:grid-cols-5">
        <section className="lg:col-span-3">
          <h2 className="mb-2 text-sm font-medium">时间节点</h2>
          {timelineReq.loading ? <Loading /> : timelineReq.error ? <ErrorState error={timelineReq.error} onRetry={() => timelineReq.reload().catch(() => {})} /> : <TimelineView timeline={timelineReq.data} />}
        </section>
        <section className="lg:col-span-2">
          <h2 className="mb-2 text-sm font-medium">审核轨迹</h2>
          {historyReq.loading ? <Loading /> : historyReq.error ? <ErrorState error={historyReq.error} onRetry={() => historyReq.reload().catch(() => {})} /> : <ReviewTrail records={Array.isArray(historyReq.data) ? historyReq.data.filter((record) => record.kind === "REVIEW").map((record, index) => ({ ...record, id: `review-${index}`, action: record.title })) : []} />}
        </section>
      </div>
    </div>
  )
}
