import { Link } from "react-router-dom"
import { FileText, ListChecks } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import StageProgress from "../../components/archive/StageProgress"
import TimelineView from "../../components/archive/TimelineView"
import { Loading, ErrorState } from "../../components/common/States"
import { StatusBadge } from "../../components/common/Badges"
import { useRequest } from "../../hooks/useRequest"
import { getTimeline, myArchive } from "../../api/archives"

export default function MyProgressPage() {
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const id = archive?.id
  const timelineReq = useRequest(() => (id ? getTimeline(id) : null), [id], { immediate: !!id })

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
      <PageHeader title="发展进度" extra={(
        <div className="flex flex-wrap gap-2">
          <Link className="btn btn-ghost btn-sm gap-2" to="/my/materials"><FileText size={15} strokeWidth={1.8} />我的材料</Link>
          {sub?.id && <Link className="btn btn-primary btn-sm gap-2" to={sub.status === "RETURNED" ? "/my/rectification" : `/my/self-check/${sub.id}`}>
            <ListChecks size={15} strokeWidth={1.8} />{sub.status === "RETURNED" ? "去整改" : "去自查"}
          </Link>}
        </div>
      )}>
        {nextAction}
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
          <StageProgress current={archive?.current_stage} stages={timelineReq.data?.stages || []} />
        </div>
      </div>
      <section className="min-w-0">
        <div className="surface-card p-4 sm:p-5">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-2 border-b border-base-200 pb-3">
            <div>
              <h2 className="text-base font-semibold">时间节点</h2>
              <p className="mt-1 text-xs text-base-content/55">按培养流程展示已识别的时间与来源材料</p>
            </div>
            {visibleNodeCount > 0 && <span className="text-xs text-base-content/50">{visibleNodeCount} 个已识别节点</span>}
          </div>
          {timelineReq.loading && !timelineReq.data ? <Loading /> : timelineReq.error ? <ErrorState error={timelineReq.error} onRetry={timelineReq.reload} /> : <TimelineView timeline={timelineReq.data} hidePersonalInfo />}
        </div>
      </section>
    </div>
  )
}
