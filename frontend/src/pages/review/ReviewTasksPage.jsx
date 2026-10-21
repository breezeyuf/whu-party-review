import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { RefreshCw } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { DemoBadge, HandoverBadge, RecoBadge, StatusBadge } from "../../components/common/Badges"
import { ErrorState } from "../../components/common/States"
import { ConfirmDialog } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { listSubmissions, batchReview } from "../../api/submissions"
import { batchAiCheck, completionNotices } from "../../api/reports"
import { daysLeftText, issueCountsText } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import ReviewJobStatus from "../../components/review/ReviewJobStatus"
import { batchReviewResult, loadReviewTasks } from "../../utils/review"

const LEVEL_OF = {
  BRANCH_REVIEWER: "BRANCH",
  CROSS_REVIEWER: "CROSS",
  COLLEGE_REVIEWER: "COLLEGE",
  ORG_ADMIN: "ORG",
}

export default function ReviewTasksPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const meta = useMeta()
  const { query, setQuery, setPage } = usePagination({ todo: "true", sort: "-submitted_at" })
  const queryKey = JSON.stringify(query)
  const roleKey = `${activeRole?.role}:${activeRole?.org_id}`
  const req = useRequest(() => loadReviewTasks(listSubmissions, query), [queryKey, roleKey])
  const [selected, setSelected] = useState([])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [batchMode, setBatchMode] = useState(false)

  useEffect(() => { setSelected([]); setResult(null) }, [queryKey, roleKey])
  useEffect(() => { setJobId(null) }, [roleKey])

  const rows = req.data?.items || []
  const toggle = (id, on) => setSelected((s) => on ? [...new Set([...s, id])] : s.filter((x) => x !== id))
  const toggleAll = (on) => setSelected((current) => on
    ? [...new Set([...current, ...rows.map((r) => r.id)])]
    : current.filter((id) => !rows.some((row) => row.id === id)))

  const level = LEVEL_OF[activeRole?.role] || "BRANCH"

  const run = async (action) => {
    if (!selected.length) { toast.info("请先勾选提交包"); return }
    setBusy(true)
    setResult(null)
    const ids = [...selected]
    try {
      if (action === "pass") {
        const summary = batchReviewResult(ids, await batchReview({ level, submission_ids: ids }))
        setSelected(summary.remaining)
        setResult({ message: `通过 ${summary.passed} 份，失败 ${summary.failures.length} 份`, items: summary.failures })
        if (summary.failures.length) toast.info("部分提交包未通过，失败项已保留勾选，请查看原因")
        else toast.success(`已通过 ${summary.passed} 份`)
      } else if (action === "completion") {
        const res = await completionNotices({ submission_ids: ids, send: true })
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
        title="审核待办"
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
        onReset={() => setQuery({ todo: "true", q: "", status: "", stage_code: "", recommendation: "", has_block: "", due_within_days: "", sort: "-submitted_at", page_size: 20 })}
        fields={[
          { key: "todo", label: "任务范围", type: "select", placeholder: "当前层级待办", options: [{ code: "true", name: "当前层级待办" }, { code: "false", name: "全部可见提交包" }] },
          { key: "q", label: "姓名 / 学号", placeholder: "搜索" },
          { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
        ]}
        advancedFields={[
          { key: "status", label: "状态", type: "select", metaKey: "submission_statuses" },
          { key: "recommendation", label: "AI 结论", type: "select", metaKey: "recommendations" },
          { key: "has_block", label: "阻断问题", type: "select", options: [{ code: "true", name: "仅看有阻断" }] },
        ]}
      /></fieldset>
      {batchMode && <div className="service-batch-toolbar" aria-label="批量操作"><span className="mr-auto text-sm">已选 {selected.length} 份</span>
        {activeRole?.role !== "CROSS_REVIEWER" && <><button type="button" className="btn btn-outline btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => run("ai")}>批量 AI 审核</button><button type="button" className="btn btn-outline btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => run("completion")}>发送补全提示</button></>}
        {level !== "ORG" && <button type="button" className="btn btn-primary btn-sm" disabled={busy || req.loading || !!req.error || !selected.length} onClick={() => run("pass")}>批量通过</button>}
        {selected.length > 0 && <button type="button" className="btn btn-ghost btn-sm" disabled={busy} onClick={() => setSelected([])}>清空选择</button>}
        <p className="w-full text-xs text-base-content/65">批量通过只处理报告有效、无阻断问题且已完成必要人工接管的提交包。</p>
      </div>}
      {jobId && <div className="mb-3"><ReviewJobStatus jobId={jobId} onDone={() => req.reload().catch(() => {})} onRetry={() => req.reload().catch(() => {})} /></div>}
      {result && <div className="surface-card mb-3 space-y-2 p-3 text-xs" role="status">
        <p className="font-medium">{result.message}</p>
        {!!result.items.length && <ul className="space-y-1">{result.items.map((item) => <li key={item.submission_id}><Link className="link" to={`/review/submissions/${item.submission_id}`}>提交包 #{item.submission_id}</Link>：{item.reason}</li>)}</ul>}
      </div>}
      {req.error && <ErrorState error={req.error} onRetry={() => req.reload().catch(() => {})} />}
      <div className="surface-card p-2">
        <div className="px-3 py-3 text-sm text-base-content/65">{req.loading ? "正在读取待办…" : `共 ${req.data?.total ?? 0} 份提交材料`}</div>
        <fieldset disabled={busy} className="min-w-0">
        <DataTable
          loading={req.loading}
          rows={rows}
          selected={batchMode ? selected : undefined}
          onToggle={batchMode ? toggle : undefined}
          onToggleAll={batchMode ? toggleAll : undefined}
          empty="没有待办"
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
            { key: "status", title: "状态", render: (r) => <StatusBadge code={r.status} /> },
            { key: "ai", title: "需要关注", sortKey: "issue_count", render: (r) => (
              <div className="flex flex-col gap-1">
                {["QUEUED", "RUNNING", "FAILED"].includes(r.ai_status) && <span className={`text-xs ${r.ai_status === "FAILED" ? "text-error" : "text-warning"}`}>{({ QUEUED: "检查排队中", RUNNING: "检查运行中", FAILED: "检查失败" })[r.ai_status]}</span>}
                <RecoBadge code={r.effective_recommendation || r.recommendation} />
                {r.handover_status === "REQUIRED" && <HandoverBadge code={r.handover_status} />}
                <span className="text-xs text-base-content/65">{issueCountsText(r.issue_counts)}</span>
              </div>
            ) },
            { key: "days", title: "截止", sortKey: "days_left", render: (r) => <span className={`text-xs ${r.days_left < 0 ? "text-error" : ""}`}>{daysLeftText(r.days_left)}</span> },
            { key: "action", title: "办理", render: (r) => <Link className="quiet-link whitespace-nowrap" to={`/review/submissions/${r.id}`}>打开材料 →</Link> },
          ]}
        />
        </fieldset>
        <div className="px-2 pb-2"><Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} /></div>
      </div>
      <ConfirmDialog
        open={confirmBatchPass}
        title="确认批量通过？"
        message={`将尝试通过已选择的 ${selected.length} 份提交包。系统仍会逐份检查审核状态、最新 AI 报告和阻断问题；不符合规则的提交包不会通过。`}
        confirmText="确认批量通过"
        busy={busy}
        onClose={() => { if (!busy) setConfirmBatchPass(false) }}
        onConfirm={async () => {
          const ok = await run(
            () => batchReview({ level, submission_ids: selected }),
            (r) => `通过 ${r.passed?.length || 0}，未通过 ${r.failed?.length || 0}`,
          )
          if (ok) setConfirmBatchPass(false)
        }}
      />
    </div>
  )
}
