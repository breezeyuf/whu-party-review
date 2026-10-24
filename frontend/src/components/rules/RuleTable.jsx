import DataTable, { Pager } from "../common/DataTable"

export default function RuleTable({ columns, rows, loading, error, onRetry, page, pageSize, total, onPage, extra }) {
  const list = Array.isArray(rows) ? rows : (rows?.items || [])
  const count = total ?? rows?.total ?? list.length
  return (
    <div className="surface-card p-2">
      {extra}
      <DataTable columns={columns} rows={list} loading={loading} error={error} onRetry={onRetry} empty="规则库暂无数据" />
      {!error && <div className="px-2 pb-2">
        <Pager page={page || rows?.page || 1} pageSize={pageSize || rows?.page_size || 20} total={count > list.length ? count : (rows?.total || 0)} onPage={onPage} />
      </div>}
    </div>
  )
}
