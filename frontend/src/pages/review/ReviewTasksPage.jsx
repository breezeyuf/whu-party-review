import { useState } from "react"
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
import { daysLeftText, fmtDateTime, issueCountsText } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"

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
  const req = useRequest(() => listSubmissions(query), [JSON.stringify(query)])
  const [selected, setSelected] = useState([])
  const [busy, setBusy] = useState(false)
  const [confirmBatchPass, setConfirmBatchPass] = useState(false)

  const rows = req.data?.items || []
  const toggle = (id, on) => setSelected((s) => on ? [...new Set([...s, id])] : s.filter((x) => x !== id))
  const toggleAll = (on) => setSelected((current) => on
    ? [...new Set([...current, ...rows.map((r) => r.id)])]
    : current.filter((id) => !rows.some((row) => row.id === id)))

  const level = LEVEL_OF[activeRole?.role] || "BRANCH"

  const run = async (fn, ok) => {
    if (!selected.length) { toast.info("请先勾选提交包"); return false }
    setBusy(true)
    try {
      const res = await fn()
      toast.success(ok(res))
      setSelected([])
      try { await req.reload() } catch { toast.info("操作已完成，但列表刷新失败；请手动刷新") }
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
        title="审核待办"
        extra={(
          <>
            <button type="button" className="btn btn-outline btn-sm" disabled={busy || !selected.length} onClick={() => run(
              () => batchAiCheck({ submission_ids: selected }),
              (r) => `已排队 ${r.total ?? selected.length} 份`,
            )}>批量 AI 审核</button>
            <button type="button" className="btn btn-outline btn-sm" disabled={busy || !selected.length} onClick={() => run(
              () => completionNotices({ submission_ids: selected, send: true }),
              (r) => `已生成 ${r.created?.length || 0} 条补全提示`,
            )}>补全提示</button>
            <button type="button" className="btn btn-primary btn-sm" disabled={busy || !selected.length} onClick={() => setConfirmBatchPass(true)}>批量通过</button>
          </>
        )}
      >
        只对最新报告无阻断问题、且人工接管已完成或不需要接管的提交包批量通过。
      </PageHeader>
      <FilterBar
        values={query}
        onChange={(patch) => setQuery(patch)}
        onReset={() => setQuery({ q: "", status: "", stage_code: "", recommendation: "", has_block: "" })}
        fields={[
          { key: "q", label: "姓名 / 学号", placeholder: "搜索" },
          { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
          { key: "status", label: "状态", type: "select", metaKey: "submission_statuses" },
          { key: "recommendation", label: "AI 结论", type: "select", metaKey: "recommendations" },
          { key: "has_block", label: "阻断问题", type: "select", options: [{ code: "true", name: "仅看有阻断" }] },
        ]}
      />
      {req.error && <ErrorState error={req.error} onRetry={req.reload} />}
      <div className="surface-card mb-2 flex flex-wrap items-center justify-between gap-2 px-3 py-2 text-xs">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-base-content/60">
          <span>符合条件 <strong className="mono text-base-content">{req.data?.total ?? "—"}</strong> 份</span>
          <span>已选择 <strong className="mono text-primary">{selected.length}</strong> 份（可跨页）</span>
        </div>
        <button type="button" className="btn btn-ghost btn-xs" disabled={req.loading} onClick={() => req.reload()}>
          <RefreshCw size={13} />刷新列表
        </button>
      </div>
      <div className="surface-card p-2">
        <DataTable
          loading={req.loading}
          rows={rows}
          selected={selected}
          onToggle={toggle}
          onToggleAll={toggleAll}
          empty={query.q || query.status || query.stage_code || query.recommendation || query.has_block ? "没有符合筛选条件的提交包" : "当前没有待处理的提交包"}
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
            { key: "ai", title: "AI", render: (r) => (
              <div className="flex flex-col gap-1">
                <RecoBadge code={r.effective_recommendation || r.recommendation} />
                <HandoverBadge code={r.handover_status} />
              </div>
            ) },
            { key: "issues", title: "问题", sortKey: "issue_count", render: (r) => <div className="text-xs"><div>{issueCountsText(r.issue_counts)}</div><div className="mt-0.5 text-base-content/50">待复核 {r.pending_count ?? 0}</div></div> },
            { key: "days", title: "截止（可排序）", sortKey: "days_left", render: (r) => {
              const cls = r.days_left == null ? "text-base-content/45" : r.days_left < 0 ? "badge-error" : r.days_left <= 3 ? "badge-warning" : "badge-ghost"
              return <span className={`badge badge-sm ${cls}`}>{daysLeftText(r.days_left)}</span>
            } },
            { key: "time", title: "提交", sortKey: "submitted_at", render: (r) => <span className="mono text-xs">{fmtDateTime(r.submitted_at)}</span> },
          ]}
        />
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
