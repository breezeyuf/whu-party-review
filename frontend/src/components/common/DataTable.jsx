import { EmptyState, ErrorState, SkeletonRows } from "./States"

// 表格区按“加载中 → 失败 → 空 → 数据”的优先级只显示一种状态
export default function DataTable({
  columns,
  rows,
  rowKey = "id",
  scrollLabel,
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
  const scrollableRows = scrollLabel && ready && rows?.length > 0

  return (
    <div
      className="overflow-x-auto outline-primary focus-visible:outline-2"
      role={scrollLabel ? "region" : undefined}
      aria-label={scrollLabel}
      tabIndex={scrollableRows ? 0 : undefined}
    >
      {scrollableRows && <p className="sticky left-0 px-3 py-1 text-xs text-base-content/65 sm:hidden">左右滑动查看更多列</p>}
      <table className="table table-compact table-zebra w-full">
        <thead>
          <tr>
            {onToggle && (
              <th className="w-8">
                <input type="checkbox" className="checkbox checkbox-xs" checked={!!allChecked} onChange={(e) => onToggleAll?.(e.target.checked)} aria-label="全选" />
              </th>
            )}
            {columns.map((col) => (
              <th key={col.key} scope="col" className={`whitespace-nowrap ${col.className || ""}`}>
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

export { default as Pager } from "./Pager"
