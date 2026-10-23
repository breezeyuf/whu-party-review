import { Link } from "react-router-dom"
import { ArrowRight, Check, Clock3, FileCheck2 } from "lucide-react"
import { dashboard } from "../../api/stats"
import { useRequest } from "../../hooks/useRequest"
import { Loading, ErrorState } from "../../components/common/States"
import StageProgress from "../../components/archive/StageProgress"
import { SeverityBadge, StatusBadge } from "../../components/common/Badges"
import { useMeta } from "../../context/MetaContext"
import { daysLeftText, fmtDate, issueCountsText, stageShort, categoryName } from "../../utils/format"
import { completeness } from "../../api/reports"
import { checklistProgress } from "../../utils/archiveWorkflow"
import { nextStudentAction } from "../../utils/workbench"
import { menusFor } from "../../utils/permissions"

export function StudentDashboard({ data }) {
  const sub = data.submission || {}
  const checklist = useRequest(() => completeness(sub.id, { live: true }), [sub.id], { immediate: !!sub.id })
  const progress = checklistProgress(checklist.data)
  const next = nextStudentAction(sub, progress)
  if (!data.archive_id) return <div className="surface-card p-6 text-sm">暂无发展档案，请联系所属支部为你建立档案。</div>
  const steps = [
    { title: "准备材料", hint: "按本阶段清单上传", to: "/my/materials" },
    { title: "自查与提交", hint: "核对问题后提交审核", to: sub.id ? `/my/self-check/${sub.id}` : "/my/materials" },
    { title: "查看审核结果", hint: sub.status === "RETURNED" ? "已退回，请完成整改" : "关注消息与发展进度", to: sub.status === "RETURNED" ? "/my/rectification" : "/my/progress" },
  ]
  return <div className="home-stack">
    <section className="next-action" aria-labelledby="student-next-action">
      <div className="next-action-context"><span>{data.stage_name || "当前发展阶段"}</span><StatusBadge code={sub.status} /></div>
      <p className="section-eyebrow">现在需要你做什么</p>
      <h2 id="student-next-action">{next.title}</h2>
      <p className="next-action-description">{next.description}</p>
      <div className="next-action-footer"><Link className="btn btn-primary" to={next.to}>{next.label}<ArrowRight size={17} /></Link><Link className="quiet-link" to="/my/progress">查看全部进度</Link></div>
    </section>
    <section className="service-section" aria-labelledby="student-process">
      <div className="section-heading"><h2 id="student-process">本阶段办理流程</h2><span className="text-sm text-base-content/65">必需材料 {checklist.loading ? "加载中…" : progress ? `${progress.actual}/${progress.expected}` : "暂无统计"}</span></div>
      {checklist.error && <div className="mb-4"><ErrorState error={checklist.error} onRetry={() => checklist.reload().catch(() => {})} /></div>}
      <ol className="process-list">{steps.map((step, index) => <li key={step.title} className={index === next.step ? "is-current" : index < next.step ? "is-complete" : ""}>
        <span className="process-number" aria-hidden="true">{index < next.step ? <Check size={17} /> : index + 1}</span>
        <div><Link to={step.to}>{step.title}</Link><p>{step.hint}</p>{index === next.step && <span className="process-current-label">当前步骤</span>}</div>
      </li>)}</ol>
    </section>
    <div className="home-support-links"><Link to="/my/rectification">整改记录<ArrowRight size={15} /></Link><Link to="/messages">查看消息<ArrowRight size={15} /></Link><span className="text-sm text-base-content/60">{issueCountsText(data.open_issues)}</span></div>
    <details className="service-details"><summary>查看发展阶段与关键日期</summary><div className="details-content"><div className="overflow-x-auto"><StageProgress current={data.current_stage} stages={sub.id ? [{ code: data.current_stage, status: sub.status, submission_id: sub.id }] : []} submissionBase="/my/self-check" /></div>{(data.timeline_preview || []).length > 0 && <dl className="mt-6 grid gap-3 sm:grid-cols-3">{data.timeline_preview.map((node) => <div key={node.code}><dt className="text-sm text-base-content/60">{node.name || node.code}</dt><dd className="mono mt-1">{fmtDate(node.date)}</dd></div>)}</dl>}</div></details>
  </div>
}

export function ReviewerDashboard({ data }) {
  const meta = useMeta()
  const todo = data.todo || {}
  const dist = data.issue_distribution || {}
  const deadlines = data.deadlines || []
  return <div className="home-stack">
    <section className="next-action reviewer-next-action" aria-labelledby="review-next-action">
      <div><p className="section-eyebrow">当前层级待办</p><h2 id="review-next-action">{todo.to_review ? <>有 <span className="mono">{todo.to_review}</span> 份材料等待审核</> : "当前没有待审核材料"}</h2><p className="next-action-description">先核对材料与问题，再作出通过或退回决定。</p><div className="next-action-footer"><Link className="btn btn-primary" to="/review/tasks">{todo.to_review ? "开始审核" : "查看审核待办"}<ArrowRight size={17} /></Link><Link className="quiet-link" to="/archives">查找学生档案</Link></div></div>
      <div className="review-todo-aside"><Link to="/review/tasks?todo=false&status=RETURNED"><Clock3 size={17} /><span>待学生整改</span><strong>{todo.returned_waiting ?? 0}</strong></Link><Link to="/review/tasks?due_within_days=7"><FileCheck2 size={17} /><span>七日内到期</span><strong>{todo.due_soon ?? 0}</strong></Link>{todo.pending_ai > 0 && <Link to="/tasks/jobs"><span>正在自动检查</span><strong>{todo.pending_ai}</strong></Link>}</div>
    </section>
    <div className="home-two-columns">
      <section className="service-section" aria-labelledby="deadline-heading"><div className="section-heading"><h2 id="deadline-heading">优先关注</h2><Link className="quiet-link text-sm" to="/review/tasks?due_within_days=7">查看全部</Link></div>{deadlines.length ? <ul className="service-task-list">{deadlines.map((deadline) => <li key={deadline.submission_id}><Link to={`/review/submissions/${deadline.submission_id}`}><span><strong>{deadline.student_name || "查看提交材料"}</strong><span className="task-hint">截止日期 {fmtDate(deadline.deadline)}</span></span><span className={deadline.days_left < 0 ? "task-status overdue" : "task-status"}>{daysLeftText(deadline.days_left)}<ArrowRight size={16} /></span></Link></li>)}</ul> : <div className="quiet-empty"><Check size={20} /><p>当前没有临近截止的事项。</p><Link className="quiet-link" to="/review/tasks">进入待办查看其他材料</Link></div>}</section>
      <aside className="service-section how-to-section"><h2>审核三步</h2><ol className="how-to-list"><li><span>1</span><div><strong>打开一份待办</strong><p>从学生姓名进入材料工作区。</p></div></li><li><span>2</span><div><strong>核对问题与原文</strong><p>点击问题定位材料，确认或驳回误报。</p></div></li><li><span>3</span><div><strong>填写审核结论</strong><p>通过、退回或按权限完成备案。</p></div></li></ol></aside>
    </div>
    <details className="service-details"><summary>查看统计与批次进度</summary><div className="details-content"><div className="mb-5"><h3 className="mb-3 font-medium">问题分布</h3><div className="flex flex-wrap gap-4 text-sm">{Object.entries(dist).map(([key, value]) => <span key={key}>{categoryName(meta, key)} <strong className="mono ml-2">{value}</strong></span>)}{!Object.keys(dist).length && <span>暂无统计</span>}</div></div><h3 className="mb-2 font-medium">批次进度</h3><p className="mb-4 text-sm text-base-content/60">{data.batch?.name || "暂无批次"}</p>{[...(data.progress?.by_stage || [])].sort((a, b) => a.stage_code - b.stage_code).map((row) => <div key={row.stage_code} className="mb-3 flex flex-wrap items-center gap-2"><span className="mr-2 font-medium">{stageShort(meta, row.stage_code)}</span>{["DRAFT", "BRANCH_REVIEW", "CROSS_REVIEW", "COLLEGE_REVIEW", "ORG_FILING", "FILED", "RETURNED"].map((key) => row[key] ? <span key={key} className="inline-flex items-center gap-1"><StatusBadge code={key} /><span className="mono text-sm">{row[key]}</span></span> : null)}</div>)}</div></details>
  </div>
}

export function AdminDashboard({ data }) {
  const management = menusFor({ role: data.role }).filter((group) => group.group === "管理").flatMap((group) => group.items)
  const descriptions = { "/admin/users": "开通账号、分配身份与维护账号状态", "/admin/orgs": "维护学院、支部与组织关系", "/admin/settings": "配置平台运行参数", "/admin/audit-logs": "查询系统操作记录", "/admin/batches": "维护发展批次与各环节截止时间" }
  return <div className="home-stack">
    <section className="next-action"><p className="section-eyebrow">管理事项</p><h2>组织与平台管理</h2><p className="next-action-description">选择需要维护的事项，进入对应管理页面。</p></section>
    <section className="admin-entry-grid" aria-label="管理功能">{management.map((item) => <Link key={item.to} className="service-section admin-entry" to={item.to}><h2>{item.label}<ArrowRight size={18} /></h2><p>{descriptions[item.to]}</p></Link>)}</section>
    {data.role === "ORG_ADMIN" && <section className="service-section"><div className="section-heading"><h2>备案办理</h2><Link className="quiet-link" to="/review/tasks">进入备案待办<ArrowRight size={16} /></Link></div><p className="text-sm text-base-content/65">当前有 <strong className="mono">{data.todo?.to_review ?? 0}</strong> 份材料等待组织部备案。</p></section>}
    <div className="home-support-links"><Link to="/stats/overview">查看审核统计<ArrowRight size={15} /></Link><Link to="/messages">查看消息<ArrowRight size={15} /></Link></div>
  </div>
}

export function DashboardBody() {
  const { data, loading, error, reload } = useRequest(() => dashboard(), [])
  if (loading && !data) return <Loading />
  if (error) return <ErrorState error={error} onRetry={() => reload().catch(() => {})} />
  if (!data) return null
  if (data.role === "STUDENT") return <StudentDashboard data={data} />
  if (data.role === "SYS_ADMIN" || data.role === "ORG_ADMIN") return <AdminDashboard data={data} />
  return <ReviewerDashboard data={data} />
}

export function SeverityInline({ counts }) {
  if (!counts) return null
  return <span className="inline-flex gap-1"><SeverityBadge code="BLOCK" /><span className="mono text-xs">{counts.BLOCK || 0}</span></span>
}
