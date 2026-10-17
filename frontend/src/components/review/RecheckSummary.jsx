export default function RecheckSummary({ summary }) {
  if (!summary) return null
  return (
    <div className="stats stats-vertical border border-base-300 bg-base-100 sm:stats-horizontal">
      <div className="stat py-2 px-4">
        <div className="stat-title text-xs">已解决</div>
        <div className="stat-value text-lg text-success">{summary.resolved ?? 0}</div>
      </div>
      <div className="stat py-2 px-4">
        <div className="stat-title text-xs">未解决</div>
        <div className="stat-value text-lg text-error">{summary.unresolved ?? 0}</div>
      </div>
      <div className="stat py-2 px-4">
        <div className="stat-title text-xs">新增</div>
        <div className="stat-value text-lg">{summary.new ?? 0}</div>
      </div>
    </div>
  )
}
