import { EmptyState, ErrorState, SkeletonRows } from "./States"

// 表格区按“加载中 → 失败 → 空 → 数据”的优先级只显示一种状态
export default function DataTable({
  columns,
  rows,
  rowKey = "id",
  loading,
  loadingLabel = "正在加载…",
  error,
  onRetry,
  empty = "暂无数据",
  emptyHint,
  emptyAction,
  sort,
  onSort,
  selected,
  onToggle,
  onToggleAll,
}) {
  const keys = selected ? new Set(selected) : new Set()
  const allChecked = keys && rows?.length > 0 && rows.every((r) => keys.has(r[rowKey]))
  const failed = !loading && !!error
  const ready = !loading && !error

  return (
    <div className="overflow-x-auto">
      <table className="table table-compact table-zebra w-full">
        <thead>
          <tr>
            {onToggle && (
              <th className="w-8">
                <input type="checkbox" className="checkbox checkbox-xs" checked={!!allChecked} onChange={(e) => onToggleAll?.(e.target.checked)} aria-label="全选" />
              </th>
            )}
            {columns.map((col) => (
              <th key={col.key} className={col.className || ""}>
                {col.sortKey ? (
                  <button type="button" className="btn btn-ghost btn-xs font-medium" onClick={() => onSort?.(col.sortKey)}>
                    {col.title}
                    {sort === col.sortKey ? " ↑" : sort === `-${col.sortKey}` ? " ↓" : ""}
                  </button>
                ) : col.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading && (
            <tr><td colSpan={columns.length + (onToggle ? 1 : 0)}>
              <div role="status" aria-live="polite"><span className="sr-only">{loadingLabel}</span><SkeletonRows rows={4} cols={Math.min(columns.length, 5)} /></div>
            </td></tr>
          )}
          {ready && rows?.map((row) => (
            <tr key={row[rowKey]} className="hover">
              {onToggle && (
                <td>
                  <input
                    type="checkbox"
                    className="checkbox checkbox-xs"
                    checked={keys.has(row[rowKey])}
                    onChange={(e) => onToggle(row[rowKey], e.target.checked)}
                    aria-label="选择行"
                  />
                </td>
              )}
              {columns.map((col) => (
                <td key={col.key} className={col.className || ""}>
                  {col.render ? col.render(row) : row[col.key] ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {failed && <ErrorState error={error} onRetry={onRetry} />}
      {ready && (!rows || rows.length === 0) && <EmptyState title={empty} hint={emptyHint} action={emptyAction} />}
    </div>
  )
}

export function Pager({ page = 1, pageSize = 20, total = 0, onPage, onPageSize }) {
  const pages = Math.max(1, Math.ceil(total / pageSize))
  if (total === 0) return null
  const start = (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  const visiblePages = Array.from({ length: Math.min(5, pages) }, (_, index) => {
    const first = Math.max(1, Math.min(page - 2, pages - 4))
    return first + index
  })
  return (
    <div className="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-base-300 px-2 pt-3 text-xs text-base-content/70">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <span className="mono">显示 {start}–{end} 条，共 {total} 条</span>
        {onPageSize && <label className="inline-flex shrink-0 items-center gap-2 whitespace-nowrap">每页
          <select className="select select-bordered select-xs" value={pageSize} onChange={(e) => onPageSize(Number(e.target.value))} aria-label="每页显示条数">
            {[10, 20, 50, 100].map((size) => <option key={size} value={size}>{size} 条</option>)}
          </select>
        </label>}
      </div>
      <nav className="flex items-center gap-1" aria-label="列表分页">
        <button type="button" className="btn btn-xs" disabled={page <= 1} onClick={() => onPage(1)} aria-label="第一页">«</button>
        <button type="button" className="btn btn-xs" disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button>
        {visiblePages.map((number) => <button key={number} type="button" className={`btn btn-xs ${number === page ? "btn-primary" : "btn-ghost"}`} aria-current={number === page ? "page" : undefined} onClick={() => onPage(number)}>{number}</button>)}
        <button type="button" className="btn btn-xs" disabled={page >= pages} onClick={() => onPage(page + 1)}>下一页</button>
        <button type="button" className="btn btn-xs" disabled={page >= pages} onClick={() => onPage(pages)} aria-label="最后一页">»</button>
      </nav>
    </div>
  )
}
