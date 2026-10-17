import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { StatusBadge } from "../../components/common/Badges"
import JobProgress from "../../components/common/JobProgress"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { getJob, listJobs, retryJob } from "../../api/jobs"
import { fmtDateTime } from "../../utils/format"

const JOB_TYPE_NAME = {
  PARSE: "材料解析",
  AI_CHECK: "AI 校验",
  BATCH_AI_CHECK: "批量 AI 校验",
  BATCH_UPLOAD: "批量上传",
  EXPORT: "数据导出",
}
import { useToast } from "../../context/ToastContext"

export default function JobsPage() {
  const toast = useToast()
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => listJobs(query), [JSON.stringify(query)])
  const [detail, setDetail] = useState(null)

  const open = async (row) => {
    setDetail(await getJob(row.id))
  }

  return (
    <div>
      <PageHeader title="任务进度" />
      <FilterBar
        values={query}
        onChange={setQuery}
        onReset={() => setQuery({ job_type: "", status: "" })}
        fields={[
          { key: "job_type", label: "类型", type: "select", options: [
            { code: "PARSE", name: "解析" },
            { code: "AI_CHECK", name: "AI 校验" },
            { code: "BATCH_AI_CHECK", name: "批量审核" },
            { code: "BATCH_UPLOAD", name: "批量上传" },
            { code: "EXPORT", name: "导出" },
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
      <div className="grid gap-4 lg:grid-cols-5">
        <div className="surface-card p-2 lg:col-span-3">
          <DataTable
            loading={req.loading}
            rows={req.data?.items || []}
            columns={[
              { key: "type", title: "类型", render: (r) => <button type="button" className="link" onClick={() => open(r)}>{JOB_TYPE_NAME[r.job_type] || r.job_type}</button> },
              { key: "status", title: "状态", render: (r) => <StatusBadge code={r.status} map={{ QUEUED: "排队", RUNNING: "运行中", SUCCEEDED: "成功", PARTIAL: "部分失败", FAILED: "失败" }} /> },
              { key: "prog", title: "进度", render: (r) => <span className="mono text-xs">{r.done_count || 0}/{r.total || "—"}{r.failed_count ? ` 失败 ${r.failed_count}` : ""}</span> },
              { key: "who", title: "发起", render: (r) => <span className="text-xs">{r.created_by_name}<br />{fmtDateTime(r.created_at)}</span> },
            ]}
          />
          <div className="px-2"><Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} /></div>
        </div>
        <aside className="lg:col-span-2 space-y-3">
          {detail ? (
            <>
              <JobProgress job={detail} onRetry={async () => { await retryJob(detail.id); toast.success("已重试"); req.reload() }} />
              {(detail.failed_children || []).length > 0 && (
                <div className="surface-card p-3 text-xs">
                  <div className="mb-2 font-medium">失败子任务</div>
                  <ul className="space-y-1">
                    {detail.failed_children.map((c) => (
                      <li key={c.id}>#{c.id} 目标 {c.target_id} · {c.error}</li>
                    ))}
                  </ul>
                </div>
              )}
              {detail.result && (
                <pre className="surface-card max-h-64 overflow-auto p-3 text-xs">{JSON.stringify(detail.result, null, 2)}</pre>
              )}
            </>
          ) : <p className="text-sm text-base-content/50">选择一条任务查看明细。</p>}
        </aside>
      </div>
    </div>
  )
}
