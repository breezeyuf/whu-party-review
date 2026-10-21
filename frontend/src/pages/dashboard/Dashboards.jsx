import { Link } from "react-router-dom"
import { dashboard } from "../../api/stats"
import { useRequest } from "../../hooks/useRequest"
import { Loading, ErrorState } from "../../components/common/States"
import StageProgress from "../../components/archive/StageProgress"
import { SeverityBadge, StatusBadge } from "../../components/common/Badges"
import { useMeta } from "../../context/MetaContext"
import { daysLeftText, fmtDate, issueCountsText, stageShort, categoryName } from "../../utils/format"

function Stat({ label, value, to }) {
  const body = (
    <div className="stat-card px-4 py-3">
      <div className="text-xs text-base-content/55">{label}</div>
      <div className="mono mt-1 text-2xl font-semibold tracking-tight">{value ?? 0}</div>
    </div>
  )
  return to ? <Link to={to} className="block">{body}</Link> : body
}

export function StudentDashboard({ data }) {
  const sub = data.submission || {}
  return (
    <div className="space-y-4">
      <div className="surface-card p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div className="text-xs text-base-content/50">当前阶段</div>
            <div className="text-lg font-semibold">{data.stage_name || "—"}</div>
          </div>
          <StatusBadge code={sub.status} />
        </div>
        <p className="mt-3 text-sm">{data.next_action || "查看材料与审核进度"}</p>
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          <span className="badge badge-ghost">清单 {data.checklist_progress?.actual ?? 0}/{data.checklist_progress?.expected ?? "—"}</span>
          <span className="badge badge-ghost">{issueCountsText(data.open_issues)}</span>
          {sub.deadline && <span className="badge badge-outline">{fmtDate(sub.deadline)}</span>}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link className="btn btn-primary btn-sm" to="/my/materials">我的材料</Link>
          {sub.id && <Link className="btn btn-outline btn-sm" to={`/my/self-check/${sub.id}`}>AI 自查</Link>}
          <Link className="btn btn-ghost btn-sm" to="/my/rectification">整改中心</Link>
        </div>
      </div>
      <div className="surface-card overflow-x-auto p-4">
        <StageProgress current={data.current_stage} stages={[]} />
      </div>
    </div>
  )
}

export function ReviewerDashboard({ data }) {
  const meta = useMeta()
  const todo = data.todo || {}
  const dist = data.issue_distribution || {}
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label="待审核" value={todo.to_review} to="/review/tasks" />
        <Stat label="待整改回传" value={todo.returned_waiting} to="/review/tasks?status=RETURNED" />
        <Stat label="AI 进行中" value={todo.pending_ai} to="/tasks/jobs" />
        <Stat label="即将到期" value={todo.due_soon} to="/review/tasks?due_within_days=3" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">问题分布</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(dist).map(([k, v]) => (
              <span key={k} className="badge badge-outline gap-2">{categoryName(meta, k)} <span className="mono">{v}</span></span>
            ))}
            {!Object.keys(dist).length && <span className="text-xs text-base-content/50">暂无</span>}
          </div>
          <ul className="mt-3 space-y-1 text-sm">
            {(data.top_rules || []).map((r) => (
              <li key={r.rule_code} className="flex justify-between gap-2" title={r.rule_code}>
                <span>{r.name}</span>
                <span className="mono">{r.count}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="surface-card p-4">
          <h2 className="mb-3 text-sm font-medium">临近截止</h2>
          <ul className="space-y-2 text-sm">
            {(data.deadlines || []).map((d) => (
              <li key={d.submission_id} className="flex items-center justify-between gap-2">
                <Link className="link" to={`/review/submissions/${d.submission_id}`}>{d.student_name}</Link>
                <span className={`text-xs ${d.days_left < 0 ? "text-error" : "text-base-content/60"}`}>{daysLeftText(d.days_left)}</span>
              </li>
            ))}
            {!(data.deadlines || []).length && <li className="text-xs text-base-content/50">没有临近事项</li>}
          </ul>
        </section>
      </div>
      <section className="surface-card p-4">
        <h2 className="mb-2 text-sm font-medium">批次进度</h2>
        <p className="mb-2 text-xs text-base-content/55">{data.batch?.name} {data.batch?.branch_deadline ? `· 支部截止 ${fmtDate(data.batch.branch_deadline)}` : ""}</p>
        {[...(data.progress?.by_stage || [])].sort((a, b) => a.stage_code - b.stage_code).map((row) => (
          <div key={row.stage_code} className="mb-2 flex flex-wrap items-center gap-1.5">
            <span className="badge badge-soft badge-sm min-w-16 justify-center">{stageShort(meta, row.stage_code)}</span>
            {["DRAFT", "BRANCH_REVIEW", "CROSS_REVIEW", "COLLEGE_REVIEW", "ORG_FILING", "FILED", "RETURNED"].map((k) => (
              row[k] ? (
                <span key={k} className="inline-flex items-center gap-1">
                  <StatusBadge code={k} />
                  <span className="mono text-xs text-base-content/55">{row[k]}</span>
                </span>
              ) : null
            ))}
          </div>
        ))}
      </section>
    </div>
  )
}

export function AdminDashboard({ data }) {
  return (
    <div className="space-y-4">
      <ReviewerDashboard data={data} />
      <div className="flex flex-wrap gap-2">
        <Link className="btn btn-outline btn-sm" to="/admin/users">用户</Link>
        <Link className="btn btn-outline btn-sm" to="/admin/orgs">组织</Link>
        <Link className="btn btn-outline btn-sm" to="/admin/batches">批次</Link>
        <Link className="btn btn-outline btn-sm" to="/admin/settings">系统配置</Link>
        <Link className="btn btn-ghost btn-sm" to="/stats/overview">统计看板</Link>
      </div>
    </div>
  )
}

export function DashboardBody() {
  const { data, loading, error, reload } = useRequest(() => dashboard(), [])
  if (loading && !data) return <Loading />
  if (error) return <ErrorState error={error} onRetry={reload} />
  if (!data) return null
  if (data.role === "STUDENT") return <StudentDashboard data={data} />
  if (data.role === "SYS_ADMIN" || data.role === "ORG_ADMIN") return <AdminDashboard data={data} />
  return <ReviewerDashboard data={data} />
}

export function SeverityInline({ counts }) {
  if (!counts) return null
  return (
    <span className="inline-flex gap-1">
      <SeverityBadge code="BLOCK" /> <span className="mono text-xs">{counts.BLOCK || 0}</span>
    </span>
  )
}
