import { useEffect, useRef, useState } from "react"
import CreatorTaskList from "../../components/common/CreatorTaskList"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { StatusBadge } from "../../components/common/Badges"
import { ErrorState, Loading } from "../../components/common/States"
import JobProgress from "../../components/common/JobProgress"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { getJob, listJobs, listJobCreators } from "../../api/jobs"
import { fmtDateTime } from "../../utils/format"
import { useToast } from "../../context/ToastContext"

const JOB_TYPE_NAME = {
  PARSE: "材料解析",
  AI_CHECK: "AI 校验",
  BATCH_AI_CHECK: "批量 AI 校验",
  BATCH_UPLOAD: "批量上传",
  EXPORT: "数据导出",
  NOTICE_BATCH: "批量补全通知",
}

export default function JobsPage() {
  const toast = useToast()
  const { query, setQuery, setPage } = usePagination({ page_size: 10 })
  const grouped = query.view !== "all"
  const { view, ...filters } = query
  const req = useRequest(() => grouped ? listJobCreators(filters) : listJobs(filters), [JSON.stringify(query)])
  const [refresh, setRefresh] = useState(0)
  // 明细请求单独管理加载与失败；快速切换任务时只采用最后一次请求的结果
  const [detail, setDetail] = useState({ id: null, data: null, loading: false, error: null })
  const sequence = useRef(0)

  const open = async (jobId) => {
    const request = ++sequence.current
    setDetail((current) => ({ id: jobId, data: current.id === jobId ? current.data : null, loading: true, error: null }))
    try {
      const data = await getJob(jobId)
      if (request === sequence.current) setDetail({ id: jobId, data, loading: false, error: null })
    } catch (error) {
      if (request === sequence.current) setDetail({ id: jobId, data: null, loading: false, error })
    }
  }

  useEffect(() => {
    sequence.current += 1
    setDetail({ id: null, data: null, loading: false, error: null })
  }, [JSON.stringify(query)])
  const columns = [
    { key: "type", title: "类型", render: (r) => <button type="button" className="link" onClick={() => open(r.id)}>{JOB_TYPE_NAME[r.job_type] || r.job_type}</button> },
    { key: "status", title: "状态", render: (r) => <StatusBadge code={r.status} map={{ QUEUED: "排队", RUNNING: "运行中", SUCCEEDED: "成功", PARTIAL: "部分失败", FAILED: "失败" }}/> },
    { key: "prog", title: "进度", render: (r) => <span className="text-xs">{r.done_count || 0}/{r.total || "—"}{r.failed_count ? ` 失败 ${r.failed_count}` : ""}</span> },
    { key: "who", title: "发起", render: (r) => <span className="text-xs">{r.created_by_name || "系统 / 历史账号"}<br/>{fmtDateTime(r.created_at)}</span> },
  ]
  const job = detail.data
  return (
    <div>
      <PageHeader title="后台任务进度" extra={<button className="btn btn-outline btn-sm" onClick={() => { setRefresh((v) => v+1); req.reload().catch(() => {}) }}>刷新任务</button>}>展开一位发起人查看任务，或切换到全部任务按时间查询。</PageHeader>
      <div className="mb-3 flex gap-2" aria-label="任务查看方式"><button className={`btn btn-sm ${grouped ? "btn-primary" : "btn-ghost"}`} onClick={() => setQuery({ view: "", page_size: 10 })}>按发起人</button><button className={`btn btn-sm ${!grouped ? "btn-primary" : "btn-ghost"}`} onClick={() => setQuery({ view: "all", page_size: 20 })}>全部任务</button></div>
      <FilterBar
        values={query}
        onChange={setQuery}
        onReset={() => setQuery({ job_type: "", status: "", q: "" })}
        fields={[
          { key: "q", label: "发起人", placeholder: "姓名或账号" },
          { key: "job_type", label: "类型", type: "select", options: [
            { code: "PARSE", name: "解析" },
            { code: "AI_CHECK", name: "AI 校验" },
            { code: "BATCH_AI_CHECK", name: "批量审核" },
            { code: "BATCH_UPLOAD", name: "批量上传" },
            { code: "EXPORT", name: "导出" },
            { code: "NOTICE_BATCH", name: "批量补全通知" },
          ] },
          { key: "status", label: "状态", type: "select", options: [
            { code: "QUEUED", name: "排队" },
            { code: "RUNNING", name: "运行" },
            { code: "SUCCEEDED", name: "成功" },
            { code: "PARTIAL", name: "部分失败" },
            { code: "FAILED", name: "失败" },
          ] },
        ]}
      />
      <div className={`grid gap-4 ${detail.id ? "lg:grid-cols-5" : ""}`}>
        <div className={`surface-card p-2 ${detail.id ? "lg:col-span-3" : ""}`}>
          {grouped ? <>
            {req.loading ? <Loading label="发起人列表"/> : req.error ? <ErrorState error={req.error} onRetry={req.reload}/> : <>
              {(req.data?.items || []).map((creator) => <CreatorTaskList key={`${JSON.stringify(query)}-${refresh}-${creator.created_by}`} creator={creator} filters={{ job_type: query.job_type, status: query.status }} columns={columns}/>)}
              {!req.data?.items?.length && <p className="p-4 text-sm text-base-content/60">没有符合条件的发起人</p>}
            </>}
          </> : <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={req.data?.items || []} empty="没有符合条件的任务" columns={columns}/>}
          {!req.error && <Pager page={req.data?.page ?? query.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} unit={grouped ? "人" : "条"} pageSizes={grouped ? [10,20,50] : [20,50,100]} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })}/>}
        </div>
        <aside className={`space-y-3 lg:col-span-2 ${!detail.id ? "hidden" : ""}`} aria-label="任务明细">
          {detail.loading && !job && <Loading label="任务明细" />}
          {detail.error && <ErrorState title="任务明细加载失败" error={detail.error} onRetry={() => open(detail.id)} />}
          {job && (
            <>
              <JobProgress job={job} onRetry={() => { toast.success("已重新排队"); setRefresh((v) => v+1); req.reload().catch(() => {}); open(job.id) }} />
              {(job.failed_children || []).length > 0 && (
                <div className="surface-card p-3 text-xs">
                  <div className="mb-2 font-medium">失败子任务</div>
                  <ul className="space-y-1">
                    {job.failed_children.map((c) => (
                      <li key={c.id}>#{c.id} 目标 {c.target_id} · {c.error}</li>
                    ))}
                  </ul>
                </div>
              )}
              {job.result && (
                <pre className="surface-card max-h-64 overflow-auto p-3 text-xs">{JSON.stringify(job.result, null, 2)}</pre>
              )}
            </>
          )}
          {!detail.id && <p className="text-sm text-base-content/50">选择一条任务查看明细。</p>}
        </aside>
      </div>
    </div>
  )
}
