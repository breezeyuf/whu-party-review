import { useState } from "react"

// 加载中、失败、空三种状态的统一提示；同一区域同一时间只显示其中一种
export function Loading({ label }) {
  return (
    <div role="status" aria-live="polite" className="flex items-center justify-center gap-3 py-16 text-sm text-base-content/60">
      <span className="loading loading-spinner loading-sm" aria-hidden="true" />
      {label ? `正在加载${label}…` : "正在加载…"}
    </div>
  )
}

// 只在请求成功且结果为空时使用：title 说明没有什么，hint 说明原因，action 放下一步操作
export function EmptyState({ title = "暂无数据", hint, action }) {
  return (
    <div className="surface-card flex flex-col items-center gap-2 px-6 py-14 text-center">
      <div className="text-sm font-medium">{title}</div>
      {hint && <p className="max-w-md text-xs text-base-content/55">{hint}</p>}
      {action}
    </div>
  )
}

export function ErrorState({ error, onRetry, title = "加载失败" }) {
  const [retrying, setRetrying] = useState(false)
  const retry = async () => {
    setRetrying(true)
    try { await onRetry() } catch { /* 新的错误由页面的请求状态展示 */ } finally { setRetrying(false) }
  }
  return (
    <div role="alert" className="alert alert-error">
      <div className="flex-1">
        <div className="text-sm font-medium">{title}</div>
        <div className="text-xs opacity-80">{error?.message || "网络异常或服务暂不可用，请稍后重试"}</div>
      </div>
      {onRetry && <button type="button" className="btn btn-sm" disabled={retrying} onClick={retry}>{retrying ? "重试中…" : "重试"}</button>}
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
