import { useState } from "react"
import { listSubmissions } from "../../api/submissions"
import { useRequest } from "../../hooks/useRequest"
import { Pager } from "../common/DataTable"
import { ErrorState, Loading } from "../common/States"

const PAGE_SIZE = 10

export default function SubmissionPicker({ selected, onChange }) {
  const [draft, setDraft] = useState("")
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const req = useRequest(() => listSubmissions({ q: search, page, page_size: PAGE_SIZE }), [search, page], { immediate: !!search })
  const selectedIds = new Set(selected.map(row => row.id))

  const find = (event) => {
    event.preventDefault()
    const next = draft.trim()
    if (next && next === search && page === 1) req.reload().catch(() => {})
    else {
      setSearch(next)
      setPage(1)
    }
  }
  const remove = id => onChange(selected.filter(row => row.id !== id))

  return <div className="space-y-2">
    <form onSubmit={find} className="flex items-end gap-2">
      <label className="min-w-0 flex-1">
        <span className="mb-1 block text-xs font-medium">学生姓名或学号</span>
        <input className="input input-bordered input-sm w-full" value={draft} onChange={e => setDraft(e.target.value)} />
      </label>
      <button type="submit" className="btn btn-outline btn-sm" disabled={!draft.trim()}>查找学生</button>
    </form>
    {search && <div aria-label="学生提交搜索结果" className="rounded-lg border border-base-300 p-2">
      {req.loading ? <Loading label="学生提交" />
        : req.error ? <ErrorState error={req.error} onRetry={() => req.reload().catch(() => {})} />
        : req.data?.items?.length ? <>
          <ul className="max-h-48 space-y-1 overflow-y-auto">
            {req.data.items.map(row => <li key={row.id}>
              <label className="flex cursor-pointer items-start gap-2 rounded px-2 py-2 hover:bg-base-200">
                <input type="checkbox" className="mt-0.5 size-4 shrink-0 accent-primary" checked={selectedIds.has(row.id)}
                  onChange={e => e.target.checked ? onChange([...selected, row]) : remove(row.id)} />
                <span className="min-w-0 text-sm">
                  {row.student_name} · {row.student_no}
                  <span className="block text-xs text-base-content/65">{[row.branch_name, row.stage_name, `提交 #${row.id}`].filter(Boolean).join(" · ")}</span>
                </span>
              </label>
            </li>)}
          </ul>
          {req.data.total > PAGE_SIZE && <Pager page={page} pageSize={PAGE_SIZE} total={req.data.total} onPage={setPage} />}
        </> : <p className="px-2 py-1 text-sm text-base-content/65">没有找到匹配的学生提交。</p>}
    </div>}
    <div aria-label="已选择的提交" className="space-y-1">
      <p role="status" className="text-xs font-medium">已选 {selected.length} 份提交</p>
      {selected.length > 0 && <ul className="max-h-36 divide-y divide-base-300 overflow-y-auto">
        {selected.map(row => <li key={row.id} className="flex items-center justify-between gap-2 text-sm">
          <span>{row.student_name} · {row.stage_name} · #{row.id}</span>
          <button type="button" aria-label={`移除${row.student_name}的提交 #${row.id}`} className="btn btn-ghost btn-xs" onClick={() => remove(row.id)}>移除</button>
        </li>)}
      </ul>}
    </div>
  </div>
}
