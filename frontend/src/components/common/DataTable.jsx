import { EmptyState, SkeletonRows } from "./States"

export default function DataTable({
  columns,
  rows,
  rowKey = "id",
  loading,
  empty = "暂无数据",
  sort,
  onSort,
  selected,
  onToggle,
  onToggleAll,
}) {
  const keys = selected ? new Set(selected) : new Set()
  const allChecked = keys && rows?.length > 0 && rows.every((r) => keys.has(r[rowKey]))

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
            <tr><td colSpan={columns.length + (onToggle ? 1 : 0)}><SkeletonRows rows={4} cols={Math.min(columns.length, 5)} /></td></tr>
          )}
          {!loading && rows?.map((row) => (
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
      {!loading && (!rows || rows.length === 0) && <EmptyState title={empty} />}
    </div>
  )
}

export function Pager({ page = 1, pageSize = 20, total = 0, onPage }) {
  const pages = Math.max(1, Math.ceil(total / pageSize))
  if (total === 0) return null
  return (
    <div className="mt-3 flex items-center justify-between text-xs text-base-content/60">
      <span className="mono">共 {total} 条 · 第 {page}/{pages} 页</span>
      <div className="join">
        <button type="button" className="btn btn-xs join-item" disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button>
        <button type="button" className="btn btn-xs join-item" disabled={page >= pages} onClick={() => onPage(page + 1)}>下一页</button>
      </div>
    </div>
  )
}
