import { useState } from "react"
import { ChevronDown } from "lucide-react"
import DataTable, { Pager } from "./DataTable"
import { useRequest } from "../../hooks/useRequest"
import { listJobs } from "../../api/jobs"
import { fmtDateTime } from "../../utils/format"

function Tasks({ creator, filters, columns }) {
  const [page, setPage] = useState(1), [size, setSize] = useState(20)
  const req = useRequest(() => listJobs({ ...filters, created_by: creator.created_by, page, page_size: size }), [JSON.stringify(filters), creator.created_by, page, size])
  return <div className="border-t border-base-300 p-3">
    <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={req.data?.items || []} columns={columns} empty="该发起人暂无符合条件的任务"/>
    {!req.error && <Pager page={req.data?.page ?? page} pageSize={req.data?.page_size ?? size} total={req.data?.total} pageSizes={[20,50,100]} onPage={setPage} onPageSize={(v) => { setSize(v); setPage(1) }}/>}</div>
}

export default function CreatorTaskList({ creator, filters, columns }) {
  const [expanded, setExpanded] = useState(false)
  return <section className="mb-3 overflow-hidden rounded-lg border border-base-300 bg-base-100">
    <button type="button" className="flex w-full flex-wrap items-center justify-between gap-3 p-4 text-left hover:bg-base-200/50" aria-expanded={expanded} onClick={() => setExpanded((v) => !v)}>
      <span className="min-w-0 break-words"><strong className="text-sm">{creator.name}</strong><span className="ml-2 text-xs text-base-content/60">{creator.username || "历史 / 系统账号"} · #{creator.created_by}</span><span className="mt-1 block text-xs text-base-content/55">最近发起 {fmtDateTime(creator.latest_at)}</span></span>
      <span className="flex items-center gap-3 whitespace-nowrap text-xs"><span>{creator.total} 项</span><span>运行 {creator.running}</span><span className={creator.failed ? "text-error" : ""}>失败 {creator.failed}</span><ChevronDown size={16} className={expanded ? "rotate-180" : ""}/></span>
    </button>
    {expanded && <Tasks creator={creator} filters={filters} columns={columns}/>}
  </section>
}
