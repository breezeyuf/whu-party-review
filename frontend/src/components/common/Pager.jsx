export default function Pager({ page = 1, pageSize = 20, total = 0, onPage, onPageSize, pageSizes = [10, 20, 50, 100], unit = "条" }) {
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
        <span className="mono">显示 {start}–{end} 条，共 {total} {unit}</span>
        {onPageSize && <label className="inline-flex shrink-0 items-center gap-2 whitespace-nowrap">每页
          <select className="select select-bordered select-xs" value={pageSize} onChange={(e) => onPageSize(Number(e.target.value))} aria-label="每页显示条数">
            {pageSizes.map((size) => <option key={size} value={size}>{size} {unit}</option>)}
          </select>
        </label>}
      </div>
      <nav className="flex flex-wrap items-center gap-1" aria-label="列表分页">
        <button type="button" className="btn btn-xs" disabled={page <= 1} onClick={() => onPage(1)} aria-label="第一页">«</button>
        <button type="button" className="btn btn-xs" disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button>
        {visiblePages.map((number) => <button key={number} type="button" className={`btn btn-xs ${number === page ? "btn-primary" : "btn-ghost"}`} aria-current={number === page ? "page" : undefined} onClick={() => onPage(number)}>{number}</button>)}
        <button type="button" className="btn btn-xs" disabled={page >= pages} onClick={() => onPage(page + 1)}>下一页</button>
        <button type="button" className="btn btn-xs" disabled={page >= pages} onClick={() => onPage(pages)} aria-label="最后一页">»</button>
      </nav>
    </div>
  )
}
