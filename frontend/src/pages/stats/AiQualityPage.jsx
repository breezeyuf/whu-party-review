import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { BarChart } from "../../components/charts/LazyCharts"
import { Loading, ErrorState, EmptyState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { aiQuality } from "../../api/stats"
import { categoryName } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"

function pct(n) {
  if (n == null) return "—"
  return `${Math.round(Number(n) * 1000) / 10}%`
}

export default function AiQualityPage() {
  const meta = useMeta()
  const [batchId, setBatchId] = useState("")
  const req = useRequest(() => aiQuality(batchId ? { batch_id: batchId } : {}), [batchId])
  const d = req.data || {}
  const byCat = Object.entries(d.by_category || {}).map(([code, n]) => ({ name: categoryName(meta, code), value: n }))

  return (
    <div>
      <PageHeader title="AI 效能评估">
        人工确认率、误报率与人工新增问题，用来衡量减负效果。数字来自审核员对 AI 问题的处置，不是预设目标。
      </PageHeader>
      <input className="input input-bordered input-sm mb-4 w-40" placeholder="批次 ID（可选）" value={batchId} onChange={(e) => setBatchId(e.target.value)} />
      {req.loading && !req.data ? <Loading /> : req.error ? <ErrorState error={req.error} onRetry={req.reload} /> : (
        <>
          <div className="stats stats-vertical mb-4 w-full border border-base-300 bg-base-100 sm:stats-horizontal">
            <div className="stat"><div className="stat-title text-xs">报告</div><div className="stat-value text-2xl">{d.reports ?? "—"}</div></div>
            <div className="stat"><div className="stat-title text-xs">核验材料</div><div className="stat-value text-2xl">{d.materials_checked ?? "—"}</div></div>
            <div className="stat"><div className="stat-title text-xs">AI 问题</div><div className="stat-value text-2xl">{d.ai_issues ?? "—"}</div></div>
            <div className="stat"><div className="stat-title text-xs">确认率</div><div className="stat-value text-2xl">{pct(d.confirm_rate)}</div></div>
            <div className="stat"><div className="stat-title text-xs">误报率</div><div className="stat-value text-2xl">{pct(d.false_positive_rate)}</div></div>
            <div className="stat"><div className="stat-title text-xs">人工新增</div><div className="stat-value text-2xl">{d.manual_added ?? "—"}</div><div className="stat-desc">漏报线索</div></div>
            <div className="stat"><div className="stat-title text-xs">一次通过率</div><div className="stat-value text-2xl">{pct(d.first_pass_rate)}</div></div>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <section className="surface-card p-4">
              <h2 className="mb-2 text-sm font-medium">按类别</h2>
              <BarChart data={byCat} />
            </section>
            <section className="surface-card p-4 text-sm">
              <h2 className="mb-2 font-medium">运行模式</h2>
              <p>仅规则命中 <span className="mono">{d.mode_ratio?.RULE_ONLY ?? 0}</span> 份</p>
              <p>规则 + 大模型 <span className="mono">{d.mode_ratio?.RULE_LLM ?? 0}</span> 份</p>
              <p className="mt-2 text-xs text-base-content/55">平均耗时 {d.avg_duration_ms != null ? `${Math.round(d.avg_duration_ms)} ms` : "—"}</p>
              <p className="text-xs text-base-content/55">已处置 {d.reviewed ?? "—"} · 确认 {d.confirmed ?? "—"} · 驳回 {d.rejected ?? "—"} · 修改 {d.modified ?? "—"}</p>
            </section>
          </div>
          <section className="surface-card mt-4 overflow-x-auto p-2">
            {!(d.by_rule || []).length ? <EmptyState title="所选范围内没有 AI 问题记录" /> : <table className="table table-sm">
              <thead><tr><th>规则</th><th>总数</th><th>确认</th><th>驳回</th><th>修改</th><th>准确度</th></tr></thead>
              <tbody>
                {(d.by_rule || []).map((r) => (
                  <tr key={r.rule_code}>
                    <td className="text-xs" title={r.rule_code}>{r.name}</td>
                    <td className="mono">{r.total}</td>
                    <td className="mono">{r.confirmed}</td>
                    <td className="mono">{r.rejected}</td>
                    <td className="mono">{r.modified}</td>
                    <td className="mono">{pct(r.precision)}</td>
                  </tr>
                ))}
              </tbody>
            </table>}
          </section>
        </>
      )}
    </div>
  )
}
