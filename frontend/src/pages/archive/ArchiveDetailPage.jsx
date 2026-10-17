import { useState } from "react"
import { Link, useParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import StageProgress from "../../components/archive/StageProgress"
import TimelineView from "../../components/archive/TimelineView"
import NodeCorrectionModal from "../../components/archive/NodeCorrectionModal"
import ReviewTrail from "../../components/review/ReviewTrail"
import { DemoBadge, StatusBadge } from "../../components/common/Badges"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { correctNode, getArchive, getHistory, getTimeline, updateArchive } from "../../api/archives"
import { fmtDate } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"

export default function ArchiveDetailPage() {
  const { id } = useParams()
  const toast = useToast()
  const { activeRole } = useAuth()
  const arch = useRequest(() => getArchive(id), [id])
  const time = useRequest(() => getTimeline(id), [id])
  const hist = useRequest(() => getHistory(id), [id])
  const [node, setNode] = useState(null)
  const [editing, setEditing] = useState(false)
  const [major, setMajor] = useState("")
  const editable = can(activeRole, "archives") && activeRole?.role !== "CROSS_REVIEWER"

  if (arch.loading && !arch.data) return <Loading />
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
          {editable && !editing && <button type="button" className="btn btn-ghost btn-xs mt-3" onClick={() => { setMajor(a.major || ""); setEditing(true) }}>编辑</button>}
          {editing && (
            <div className="mt-3 flex gap-2">
              <input className="input input-bordered input-xs" value={major} onChange={(e) => setMajor(e.target.value)} placeholder="专业" />
              <button type="button" className="btn btn-primary btn-xs" onClick={async () => { await updateArchive(id, { major }); setEditing(false); arch.reload() }}>保存</button>
            </div>
          )}
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
          <TimelineView timeline={time.data} onCorrect={editable ? setNode : undefined} />
        </section>
      </div>
      <h2 className="mb-2 text-sm font-medium">审核与整改历史</h2>
      <ReviewTrail records={Array.isArray(hist.data) ? hist.data : []} />
      {node && (
        <NodeCorrectionModal
          node={node}
          onClose={() => setNode(null)}
          onSave={(body) => correctNode(id, node.code, body).then(() => { toast.success("已校正"); time.reload() })}
        />
      )}
    </div>
  )
}
