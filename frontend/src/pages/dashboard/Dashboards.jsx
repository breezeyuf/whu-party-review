import { Link } from "react-router-dom"
import { ArrowRight, Check, Clock3, FileCheck2 } from "lucide-react"
import { dashboard } from "../../api/stats"
import { useRequest } from "../../hooks/useRequest"
import { Loading, ErrorState } from "../../components/common/States"
import { SeverityBadge, StatusBadge } from "../../components/common/Badges"
import { useMeta } from "../../context/MetaContext"
import { daysLeftText, fmtDate, stageShort, categoryName } from "../../utils/format"
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
    { title: sub.status === "RETURNED" ? "整改与重新提交" : "自查与提交", hint: sub.status === "RETURNED" ? "按退回意见补充材料与说明" : "核对问题后提交审核", to: sub.status === "RETURNED" ? "/my/rectification" : sub.id ? `/my/self-check/${sub.id}` : "/my/materials" },
    { title: "查看审核结果", hint: sub.status === "RETURNED" ? "已退回，请完成整改" : "关注消息与发展进度", to: sub.status === "RETURNED" ? "/my/rectification" : "/my/progress" },
  ]
  return <div className="home-stack">
    <section className="next-action" aria-labelledby="student-next-action">
      <div className="next-action-context"><span>{data.stage_name || "当前发展阶段"}</span><StatusBadge code={sub.status} /></div>
      <p className="section-eyebrow">现在需要你做什么</p>
      <h2 id="student-next-action">{next.title}</h2>
      <p className="next-action-description">{next.description}</p>
      <div className="next-action-footer"><Link className="btn btn-primary" to={next.to}>{next.label}</Link></div>
    </section>
    <section className="service-section" aria-labelledby="student-process">
      <div className="section-heading"><h2 id="student-process">本阶段办理流程</h2><span className="text-sm text-base-content/65">必需材料 {checklist.loading ? "加载中…" : progress ? `${progress.actual}/${progress.expected}` : "暂无统计"}</span></div>
      {checklist.error && <div className="mb-4"><ErrorState error={checklist.error} onRetry={() => checklist.reload().catch(() => {})} /></div>}
      <ol className="process-list">{steps.map((step, index) => <li key={step.title} className={index === next.step ? "is-current" : index < next.step ? "is-complete" : ""}>
        <span className="process-number" aria-hidden="true">{index < next.step ? <Check size={17} /> : index + 1}</span>
        <div><Link to={step.to}>{step.title}</Link><p>{step.hint}</p>{index === next.step && <span className="process-current-label">当前步骤</span>}</div>
      </li>)}</ol>
    </section>
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
  const org = data.role === "ORG_ADMIN"
  const allowed = new Map(menusFor({ role: data.role }).flatMap(group => group.items).map(entry => [entry.to, entry]))
  const entries = (paths) => paths.filter(([to]) => allowed.has(to))
  const main = entries(org ? [
    ["/archives", "发展档案", "查询学生材料与办理进度"],
    ["/admin/batches", "发展批次", "安排批次与各环节截止时间"],
    ["/stats/overview", "审核统计", "查看各组织的审核与整改情况"],
  ] : [
    ["/admin/users", "用户管理", "开通账号与维护授权身份"],
    ["/admin/orgs", "组织架构", "维护学院、支部与组织关系"],
    ["/admin/settings", "系统配置", "配置识别服务与平台运行参数"],
    ["/admin/audit-logs", "操作日志", "追查账号操作与配置变更"],
  ])
  return <div className="home-stack">
    {org && <section className="next-action" aria-labelledby="filing-next-action">
      <p className="section-eyebrow">当前备案待办</p>
      <h2 id="filing-next-action">{data.todo?.to_review == null ? "查看待备案材料" : data.todo.to_review ? `${data.todo.to_review} 份材料等待备案` : "当前没有待备案材料"}</h2>
      <p className="next-action-description">核对原文、处理问题，再填写备案或退回结论。</p>
      <div className="next-action-footer"><Link className="btn btn-primary" to="/review/tasks">进入备案待办</Link></div>
    </section>}
    <section aria-label={org ? "日常办理" : "管理功能"}>
      <h2 className="mb-3 text-sm font-semibold">{org ? "日常办理" : "账号与平台管理"}</h2>
      <div className={`admin-entry-grid ${org ? "" : "admin-entry-grid--system"}`}>{main.map(([to, title, description]) => <Link key={to} className="service-section admin-entry" to={to}><h3 className="text-base font-semibold">{title}</h3><p>{description}</p></Link>)}</div>
    </section>
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
