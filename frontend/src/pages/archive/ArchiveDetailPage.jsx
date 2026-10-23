import { Suspense, useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import StageProgress from "../../components/archive/StageProgress"
import TimelineView from "../../components/archive/TimelineView"
import ReviewTrail from "../../components/review/ReviewTrail"
import { DemoBadge, StatusBadge } from "../../components/common/Badges"
import { Loading, ErrorState } from "../../components/common/States"
import { ModalLoading } from "../../components/common/Modal"
import { lazyWithRetry, whenIdle } from "../../utils/lazyLoad"
import { useRequest } from "../../hooks/useRequest"
import { correctNode, getArchive, getHistory, getTimeline, updateArchive } from "../../api/archives"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { canManageArchive } from "../../utils/archiveWorkflow"
import ArchiveProfileForm from "../../components/archive/ArchiveProfileForm"

// 节点校正弹窗只在校正时使用，不进页面首屏
const NodeCorrectionModal = lazyWithRetry(() => import("../../components/archive/NodeCorrectionModal"))

export default function ArchiveDetailPage() {
  const { id } = useParams()
  const toast = useToast()
  const { activeRole } = useAuth()
  const arch = useRequest(() => getArchive(id), [id])
  const time = useRequest(() => getTimeline(id), [id])
  const hist = useRequest(() => getHistory(id), [id])
  const [node, setNode] = useState(null)
  const [editing, setEditing] = useState(false)
  const editable = canManageArchive(activeRole)
  useEffect(() => (editable ? whenIdle(() => NodeCorrectionModal.preload().catch(() => {}), 0) : undefined), [editable])

  const save = async (body) => {
      await updateArchive(id, body)
      toast.success("档案已保存")
      setEditing(false)
      await Promise.all([arch.reload(), time.reload()])
  }

  if (arch.loading && !arch.data) return <Loading label="发展档案" />
  if (arch.error) return <ErrorState error={arch.error} onRetry={arch.reload} />
  const a = arch.data
  if (!a) return null

  return (
    <div>
      <PageHeader
        title={a.real_name || a.student?.real_name || "发展档案"}
        crumbs={[{ label: "发展档案", to: "/archives" }, { label: "详情" }]}
        extra={<><DemoBadge show={a.is_demo} /><StatusBadge code={a.status} /></>}
      >
        {a.student_no} · {a.branch_name || a.branch?.name} · {a.batch_name || a.batch?.name}
      </PageHeader>
      <div className="surface-card mb-4 overflow-x-auto p-4">
        <StageProgress current={a.current_stage} stages={time.data?.stages || a.submissions?.map((s) => ({ code: s.stage_code, status: s.status, submission_id: s.id })) || []} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <section className="surface-card p-4 text-sm lg:col-span-1">
          <h2 className="mb-2 font-medium">基本信息</h2>
          <dl className="grid grid-cols-[5rem_1fr] gap-y-1 text-xs">
            <dt className="text-base-content/50">性别</dt><dd>{a.gender || "—"}</dd>
            <dt className="text-base-content/50">民族</dt><dd>{a.ethnicity || "—"}</dd>
            <dt className="text-base-content/50">出生</dt><dd>{fmtDate(a.birth_date)}</dd>
            <dt className="text-base-content/50">籍贯</dt><dd>{a.native_place || "—"}</dd>
            <dt className="text-base-content/50">专业</dt><dd>{a.major || "—"}</dd>
            <dt className="text-base-content/50">班级</dt><dd>{a.class_name || "—"}</dd>
            <dt className="text-base-content/50">手机</dt><dd>{a.phone_masked || "—"}</dd>
            <dt className="text-base-content/50">证件</dt><dd>{a.id_card_masked || "—"}</dd>
          </dl>
          {editable && !editing && <button type="button" className="btn btn-ghost btn-xs mt-3" onClick={() => setEditing(true)}>编辑</button>}
          {editing && <ArchiveProfileForm archive={a} onSave={save} onCancel={() => setEditing(false)} />}
          <h3 className="mb-2 mt-4 text-sm font-medium">各阶段提交包</h3>
          <ul className="space-y-1 text-xs">
            {(a.submissions || []).map((s) => (
              <li key={s.id} className="flex items-center justify-between">
                <Link className="link" to={`/review/submissions/${s.id}`}>阶段 {s.stage_code} · 第 {s.round_no} 轮</Link>
                <StatusBadge code={s.status} />
              </li>
            ))}
          </ul>
        </section>
        <section className="lg:col-span-2">
          <h2 className="mb-2 text-sm font-medium">时间节点</h2>
          {time.error ? <ErrorState error={time.error} onRetry={() => time.reload().catch(() => {})} /> : time.loading && !time.data ? <Loading /> : <>
            <TimelineView timeline={time.data} allowLockedCorrection={activeRole?.role === "ORG_ADMIN"} onCorrect={editable ? setNode : undefined} />
            {time.data?.report_is_stale && <p className="mt-3 text-xs text-warning">时间节点已变更，请重新校验报告。</p>}
          </>}
        </section>
      </div>
      <h2 className="mb-2 text-sm font-medium">审核与整改历史</h2>
      {hist.error ? <ErrorState error={hist.error} onRetry={() => hist.reload().catch(() => {})} /> : hist.loading && !hist.data ? <Loading /> : <ReviewTrail records={Array.isArray(hist.data) ? hist.data : []} />}
      {node && (
        <Suspense fallback={<ModalLoading />}><NodeCorrectionModal
          key={node.code}
          node={node}
          onClose={() => setNode(null)}
          onSave={(body) => correctNode(id, node.code, body).then(() => { toast.success("已校正，请重新校验受影响的报告"); time.reload().catch(() => {}); arch.reload().catch(() => {}) })}
        /></Suspense>
      )}
    </div>
  )
}
