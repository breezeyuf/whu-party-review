import { reviewMessage } from "../../utils/reviewTerms"
import { Suspense, useEffect, useState } from "react"
import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { DemoBadge, HandoverBadge, RecoBadge, StatusBadge } from "../../components/common/Badges"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { listSubmissions, batchReview } from "../../api/submissions"
import { batchAiCheck, completionNotices } from "../../api/reports"
import { daysLeftText, issueCountsText } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { batchReviewResult, loadReviewTasks, PASS_RULE_TEXT, reviewQueryErrorText } from "../../utils/review"
import { lazyWithRetry } from "../../utils/lazyLoad"

// 只在批量处理时用到：进入批量模式时预取，不进待办首屏
const ReviewJobStatus = lazyWithRetry(() => import("../../components/review/ReviewJobStatus"))
const ConfirmDialog = lazyWithRetry(() => import("../../components/common/Modal").then((m) => ({ default: m.ConfirmDialog })))

const LEVEL_OF = {
  BRANCH_REVIEWER: "BRANCH",
  CROSS_REVIEWER: "CROSS",
  COLLEGE_REVIEWER: "COLLEGE",
  ORG_ADMIN: "ORG",
}

const DEFAULT_QUERY = { todo: "true", sort: "-submitted_at" }
// 这些条件有值时，空结果提示“没有符合筛选条件的提交包”并提供清除
const FILTER_KEYS = ["q", "status", "stage_code", "recommendation", "has_block", "due_within_days", "batch_id", "branch_id", "level", "min_issues"]
const BLOCK_OPTIONS = [{ code: "true", name: "仅看有关键问题" }, { code: "false", name: "仅看无关键问题" }]
const DUE_OPTIONS = [
  { code: "0", name: "今天到期或已逾期" },
  { code: "3", name: "3 天内" },
  { code: "7", name: "7 天内" },
  { code: "14", name: "14 天内" },
]

// 地址栏里的其他截止天数（如首页链接或手工输入）也要在下拉框中显示出来，便于看清和清除
function dueOptions(value) {
  if (value == null || value === "" || DUE_OPTIONS.some((option) => option.code === String(value))) return DUE_OPTIONS
  const text = String(value)
  return [...DUE_OPTIONS, { code: text, name: /^\d+$/.test(text) ? `${Number(text)} 天内` : `无效值：${text}` }]
}

export default function ReviewTasksPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const meta = useMeta()
  const { query, setQuery, setPage } = usePagination(DEFAULT_QUERY)
  const queryKey = JSON.stringify(query)
  const roleKey = `${activeRole?.role}:${activeRole?.org_id}`
  const req = useRequest(() => loadReviewTasks(listSubmissions, query), [queryKey, roleKey])
  const [selected, setSelected] = useState([])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [batchMode, setBatchMode] = useState(false)
  const [confirmBatchPass, setConfirmBatchPass] = useState(false)

  useEffect(() => { setSelected([]); setResult(null) }, [queryKey, roleKey])
  useEffect(() => { setJobId(null) }, [roleKey])
  useEffect(() => {
    if (!batchMode) return
    ConfirmDialog.preload().catch(() => {})
    ReviewJobStatus.preload().catch(() => {})
  }, [batchMode])

  const rows = req.data?.items || []
  const toggle = (id, on) => setSelected((s) => on ? [...new Set([...s, id])] : s.filter((x) => x !== id))
  const toggleAll = (on) => setSelected((current) => on
    ? [...new Set([...current, ...rows.map((r) => r.id)])]
    : current.filter((id) => !rows.some((row) => row.id === id)))

  const level = LEVEL_OF[activeRole?.role] || "BRANCH"
  const filtered = FILTER_KEYS.some((key) => query[key] != null && query[key] !== "")
  // 重置同时清除筛选栏未显示、但可能来自链接的条件（如 batch_id）
  const reset = () => setQuery({ ...Object.fromEntries(FILTER_KEYS.map((key) => [key, ""])), todo: "true", sort: "-submitted_at" })
  const loadError = req.error ? { ...req.error, message: reviewQueryErrorText(req.error) } : null
  const empty = filtered
    ? { title: "没有符合筛选条件的提交包", hint: "可以放宽或清除筛选条件后再查看。", action: <button type="button" className="btn btn-outline btn-sm" onClick={reset}>清除筛选条件</button> }
    : query.todo === "false"
      ? { title: "当前没有可见的提交包" }
      : { title: "当前层级没有待办", hint: "新提交或流转到本层级的材料会出现在这里。" }

  const run = async (action) => {
    if (!selected.length) { toast.info("请先勾选提交包"); return }
    setBusy(true)
    setResult(null)
    const ids = [...selected]
    try {
      if (action === "pass") {
        const summary = batchReviewResult(ids, await batchReview({ level, submission_ids: ids }))
        setSelected(summary.remaining)
        setResult({ message: `通过 ${summary.passed} 份，未通过 ${summary.failures.length} 份`, items: summary.failures })
        if (summary.failures.length) toast.info("部分提交包未通过，未通过的已保留勾选，请查看原因")
        else toast.success(`已通过 ${summary.passed} 份`)
      } else if (action === "completion") {
        const res = await completionNotices({ submission_ids: ids, send: true, background: true })
        if (res.job_id) {
          setJobId(res.job_id)
          setResult({ message: `已排队 ${res.total ?? ids.length} 份补全提示`, items: [] })
          toast.info("补全提示已交由后台处理，可在任务列表查看结果")
          setSelected([])
          return true
        }
        setResult({ message: `已发送 ${res.created?.length || 0} 条补全提示，跳过 ${res.skipped?.length || 0} 份`, items: res.skipped || [] })
        toast.success(`已发送 ${res.created?.length || 0} 条补全提示`)
        setSelected([])
      } else {
        const res = await batchAiCheck({ submission_ids: ids })
        setJobId(res.job_id)
        const queued = res.total ?? ids.length
        setResult({ message: `已排队 ${queued} 份 AI 审核${queued < ids.length ? "；部分选中项当前不可检查，保留勾选以便核实" : ""}`, items: [] })
        if (queued === ids.length) setSelected([])
        toast.info(`已排队 ${queued} 份 AI 审核`)
      }
      await req.reload().catch(() => {})
      return true
    } catch (e) {
      toast.error(e.message || "操作失败")
      return false
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <PageHeader
        title={level === "ORG" ? "备案待办" : "审核待办"}
        extra={(
          <>
            <button type="button" className="btn btn-outline btn-sm" aria-pressed={batchMode} disabled={busy} onClick={() => { setBatchMode((value) => !value); setSelected([]) }}>{batchMode ? "退出批量处理" : "批量处理"}</button>
            <button type="button" className="btn btn-ghost btn-sm" disabled={busy || req.loading} onClick={() => req.reload().catch(() => {})}>刷新</button>
          </>
        )}
      >
        {level === "ORG" ? "打开一份材料，核对问题后完成备案。" : "点击学生姓名开始审核。需要同时处理多份时，选择“批量处理”。"}
      </PageHeader>
      <fieldset disabled={busy} className="min-w-0"><FilterBar
        values={query}
        onChange={(patch) => setQuery(patch)}
        onReset={reset}
        fields={[
          { key: "todo", label: "任务范围", type: "select", placeholder: "当前层级待办", options: [{ code: "true", name: "当前层级待办" }, { code: "false", name: "全部可见提交包" }] },
          { key: "q", label: "姓名 / 学号", placeholder: "搜索" },
          { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
        ]}
        advancedFields={[
          { key: "status", label: "状态", type: "select", metaKey: "submission_statuses" },
          { key: "recommendation", label: "AI 结论", type: "select", metaKey: "recommendations" },
          { key: "has_block", label: "关键问题", type: "select", options: BLOCK_OPTIONS },
          { key: "due_within_days", label: "截止", type: "select", options: dueOptions(query.due_within_days) },
        ]}
      /></fieldset>
      {batchMode && <div className="service-batch-toolbar" aria-label="批量操作"><span className="mr-auto text-sm">已选 {selected.length} 份</span>
        {activeRole?.role !== "CROSS_REVIEWER" && <><button type="button" className="btn btn-outline btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => run("ai")}>批量 AI 审核</button><button type="button" className="btn btn-outline btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => run("completion")}>发送补全提示</button></>}
        {level !== "ORG" && <button type="button" className="btn btn-primary btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => setConfirmBatchPass(true)}>批量通过</button>}
        {selected.length > 0 && <button type="button" className="btn btn-ghost btn-sm" disabled={busy} onClick={() => setSelected([])}>清空选择</button>}
        <p className="w-full text-xs text-base-content/65">批量通过逐份执行与单份通过相同的校验：AI 报告须有效，必要的人工接管须已完成。{PASS_RULE_TEXT}</p>
      </div>}
      {jobId && <div className="mb-3"><Suspense fallback={<p className="text-xs text-base-content/60" role="status">正在加载任务状态…</p>}><ReviewJobStatus jobId={jobId} onDone={() => req.reload().catch(() => {})} onRetry={() => req.reload().catch(() => {})} /></Suspense></div>}
      {result && <div className="surface-card mb-3 space-y-2 p-3 text-xs" role="status">
        <p className="font-medium">{result.message}</p>
        {!!result.items.length && <ul className="space-y-1">{result.items.map((item) => <li key={item.submission_id}><Link className="link" to={`/review/submissions/${item.submission_id}`}>提交包 #{item.submission_id}</Link>：{reviewMessage(item.reason)}</li>)}</ul>}
      </div>}
      <div className="surface-card p-2">
        {!req.error && <div className="px-3 py-3 text-sm text-base-content/65" role="status" aria-live="polite">{req.loading ? "正在加载待办…" : `共 ${req.data?.total ?? 0} 份提交材料`}</div>}
        <fieldset disabled={busy} className="min-w-0">
        <DataTable
          loading={req.loading}
          loadingLabel="正在加载待办…"
          error={loadError}
          onRetry={req.reload}
          rows={rows}
          selected={batchMode ? selected : undefined}
          onToggle={batchMode ? toggle : undefined}
          onToggleAll={batchMode ? toggleAll : undefined}
          empty={empty.title}
          emptyHint={empty.hint}
          emptyAction={empty.action}
          sort={query.sort}
          onSort={(key) => setQuery({ sort: query.sort === key ? `-${key}` : key })}
          columns={[
            { key: "student", title: "学生", render: (r) => (
              <div>
                <Link className="link font-medium" to={`/review/submissions/${r.id}`}>{r.student_name}</Link>
                <DemoBadge show={r.is_demo} />
                <div className="mono text-xs text-base-content/50">{r.student_no} · {r.branch_name}</div>
              </div>
            ) },
            { key: "stage", title: "阶段", render: (r) => r.stage_name || (meta.stages || []).find((s) => s.code === r.stage_code)?.name },
            { key: "status", title: "状态", render: (r) => <StatusBadge code={r.status} soft /> },
            { key: "ai", title: "需要关注", sortKey: "issue_count", render: (r) => (
              <div className="flex flex-col gap-1">
                {["QUEUED", "RUNNING", "FAILED"].includes(r.ai_status) && <span className={`text-xs ${r.ai_status === "FAILED" ? "text-error" : "text-warning"}`}>{({ QUEUED: "检查排队中", RUNNING: "检查运行中", FAILED: "检查失败" })[r.ai_status]}</span>}
                <RecoBadge code={r.effective_recommendation || r.recommendation} soft />
                {r.handover_status === "REQUIRED" && <HandoverBadge code={r.handover_status} soft />}
                <span className="text-xs text-base-content/65">{issueCountsText(r.issue_counts)}</span>
              </div>
            ) },
            { key: "days", title: "截止", sortKey: "days_left", render: (r) => <span className={`text-xs ${r.days_left < 0 ? "text-error" : ""}`}>{daysLeftText(r.days_left)}</span> },
            { key: "action", title: "办理", render: (r) => <Link className="quiet-link whitespace-nowrap" to={`/review/submissions/${r.id}`}>打开材料 →</Link> },
          ]}
        />
        </fieldset>
        {!req.error && <div className="px-2 pb-2"><Pager page={req.data?.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })} /></div>}
      </div>
      {confirmBatchPass && <Suspense fallback={null}><ConfirmDialog
        open={confirmBatchPass}
        title="确认批量通过？"
        message={`将逐份通过已选择的 ${selected.length} 份提交包，每份都按单份通过的同一套规则检查审核状态、AI 报告、关键问题和人工接管。${PASS_RULE_TEXT}未通过的提交包会保留勾选并显示原因。`}
        confirmText="确认批量通过"
        busy={busy}
        onClose={() => { if (!busy) setConfirmBatchPass(false) }}
        onConfirm={async () => {
          const ok = await run("pass")
          if (ok) setConfirmBatchPass(false)
        }}
      /></Suspense>}
    </div>
  )
}
