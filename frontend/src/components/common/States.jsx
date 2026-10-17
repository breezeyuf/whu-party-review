export function Loading({ label = "加载中" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-sm text-base-content/60">
      <span className="loading loading-spinner loading-sm" />
      {label}
    </div>
  )
}

export function EmptyState({ title = "暂无数据", hint, action }) {
  return (
    <div className="surface-card flex flex-col items-center gap-2 px-6 py-14 text-center">
      <div className="text-sm font-medium">{title}</div>
      {hint && <p className="max-w-md text-xs text-base-content/55">{hint}</p>}
      {action}
    </div>
  )
}

export function ErrorState({ error, onRetry }) {
  return (
    <div className="alert alert-error">
      <div className="flex-1">
        <div className="text-sm font-medium">加载失败</div>
        <div className="text-xs opacity-80">{error?.message || "请稍后重试"}</div>
      </div>
      {onRetry && <button type="button" className="btn btn-sm" onClick={onRetry}>重试</button>}
    </div>
  )
}

export function SkeletonRows({ rows = 5, cols = 4 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="grid gap-2" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0,1fr))` }}>
          {Array.from({ length: cols }).map((__, j) => (
            <div key={j} className="h-8 animate-pulse rounded bg-base-200" />
          ))}
        </div>
      ))}
    </div>
  )
}
