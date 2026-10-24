import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import { BarChart, LineChart, PieChart } from "../../components/charts/LazyCharts"
import { Loading, ErrorState, EmptyState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { overview, topIssues } from "../../api/stats"
import { listBatches } from "../../api/batches"
import { categoryName, severityName, stageShort } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"

function Card({ title, value, hint }) {
  return (
    <div className="stat">
      <div className="stat-title text-xs">{title}</div>
      <div className="stat-value text-2xl">{value ?? "—"}</div>
      {hint && <div className="stat-desc">{hint}</div>}
    </div>
  )
}

export default function StatsOverviewPage() {
  const meta = useMeta()
  const batches = useRequest(() => listBatches({ page_size: 200 }), [])
  const [filters, setFilters] = useState({})
  const dataReq = useRequest(() => overview(filters), [JSON.stringify(filters)])
  const topReq = useRequest(() => topIssues({ ...filters, limit: 10, group_by: "rule" }), [JSON.stringify(filters)])
  const d = dataReq.data || {}

  const pie = Object.entries(d.issues_by_category || {}).map(([k, v]) => ({ name: categoryName(meta, k), value: v }))
  const sev = Object.entries(d.issues_by_severity || {}).map(([k, v]) => ({ name: severityName(meta, k), value: v }))
  const byBranch = (d.by_branch || []).map((b) => ({ name: b.branch_name, value: b.submissions }))
  const byStage = (d.by_stage || []).map((s) => ({ name: stageShort(meta, s.stage_code), value: s.submissions }))

  return (
    <div>
      <PageHeader title="审核统计" />
      <FilterBar
        values={filters}
        onChange={(p) => setFilters((f) => ({ ...f, ...p }))}
        onReset={() => setFilters({})}
        fields={[
          { key: "batch_id", label: "批次", type: "select", options: (batches.data?.items || []).map((b) => ({ code: b.id, name: b.name })) },
          { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
          { key: "date_from", label: "开始", placeholder: "YYYY-MM-DD" },
          { key: "date_to", label: "结束", placeholder: "YYYY-MM-DD" },
        ]}
      />
      {dataReq.loading && !dataReq.data ? <Loading /> : dataReq.error ? <ErrorState error={dataReq.error} onRetry={dataReq.reload} /> : (
        <>
          <div className="stats stats-vertical mb-4 w-full border border-base-300 bg-base-100 sm:stats-horizontal">
            <Card title="档案" value={d.archives} />
            <Card title="提交包" value={d.submissions} />
            <Card title="材料" value={d.materials} />
            <Card title="问题" value={d.issues_total} />
            <Card title="退回率" value={d.return_rate != null ? `${Math.round(d.return_rate * 100)}%` : "—"} />
            <Card title="平均整改轮次" value={d.avg_rectification_rounds != null ? Number(d.avg_rectification_rounds).toFixed(1) : "—"} />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <section className="surface-card p-4">
              <h2 className="mb-2 text-sm font-medium">问题类别</h2>
              <PieChart data={pie} />
            </section>
            <section className="surface-card p-4">
              <h2 className="mb-2 text-sm font-medium">问题级别</h2>
              <PieChart data={sev} />
            </section>
            <section className="surface-card p-4">
              <h2 className="mb-2 text-sm font-medium">各支部提交量</h2>
              <BarChart data={byBranch} />
            </section>
            <section className="surface-card p-4">
              <h2 className="mb-2 text-sm font-medium">各阶段提交量</h2>
              <PieChart data={byStage} />
            </section>
            <section className="surface-card p-4 lg:col-span-2">
              <h2 className="mb-2 text-sm font-medium">流转趋势</h2>
              {(d.trend || []).length
                ? <LineChart data={d.trend} lines={[{ key: "submitted", name: "提交" }, { key: "passed", name: "通过" }, { key: "returned", name: "退回" }]} />
                : <p className="py-16 text-center text-xs text-base-content/45">所选范围内暂无流转记录（演示数据未生成审核流水）</p>}
            </section>
          </div>
          <section className="surface-card mt-4 p-4">
            <h2 className="mb-2 text-sm font-medium">高频问题</h2>
            {topReq.loading && !topReq.data ? <Loading label="高频问题" /> : topReq.error ? <ErrorState error={topReq.error} onRetry={topReq.reload} /> : !(topReq.data || []).length ? <EmptyState title="所选范围内没有问题记录" /> : (
              <table className="table table-sm">
                <thead><tr><th>规则</th><th>次数</th><th>占比</th><th>已确认</th></tr></thead>
                <tbody>
                  {(topReq.data || []).map((r) => (
                    <tr key={r.key}><td className="text-xs" title={r.key}>{r.name}</td><td className="mono">{r.count}</td><td className="mono">{r.ratio != null ? `${Math.round(r.ratio * 100)}%` : "—"}</td><td className="mono">{r.confirmed_count ?? "—"}</td></tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  )
}
