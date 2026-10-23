import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import StatsFilters from "../../components/charts/StatsFilters"
import JobProgress from "../../components/common/JobProgress"
import { useJobPolling } from "../../hooks/useJobPolling"
import { downloadExport, exportStats } from "../../api/stats"
import { saveBlob } from "../../api/client"
import { validDate } from "../../utils/adminWorkflow"

export default function ExportPage() {
  const [filters, setFilters] = useState({})
  const [type, setType] = useState("STATS_REPORT")
  const [jobId, setJobId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const { job, error: jobError } = useJobPolling(jobId)
  const start = async () => {
    if (busy || ["QUEUED", "RUNNING"].includes(job?.status)) return
    setError("")
    try {
      if ([filters.date_from, filters.date_to].some((v) => v && !validDate(v)) || (filters.date_from && filters.date_to && filters.date_from > filters.date_to)) throw new Error("请填写有效的起止日期")
      setBusy(true)
      const result = await exportStats({ export_type: type, filters: Object.fromEntries(Object.entries(filters).filter(([,v]) => v !== "")) })
      setJobId(result.job_id)
    } catch (e) { setError(e.message || "导出失败") } finally { setBusy(false) }
  }
  const download = async () => {
    setError(""); setBusy(true)
    try { saveBlob(await downloadExport(job.result.export_id)) } catch (e) { setError(e.message || "下载失败") } finally { setBusy(false) }
  }
  return <div>
    <PageHeader title="数据导出">按有权访问的组织和筛选条件生成报表，下载操作留有审计记录。</PageHeader>
    <StatsFilters value={filters} onChange={setFilters} exportMode />
    <div className="surface-card space-y-3 p-4"><label className="form-control text-xs">类型<select aria-label="导出类型" className="select select-bordered select-sm mt-1 max-w-sm" value={type} onChange={(e) => setType(e.target.value)}><option value="STATS_REPORT">统计报表</option><option value="DESENSITIZED_DATA">去隐私审核数据</option><option value="AI_QUALITY">AI 效能</option></select></label><button type="button" className="btn btn-primary btn-sm" disabled={busy || ["QUEUED","RUNNING"].includes(job?.status)} onClick={start}>{busy ? "处理中…" : "生成 Excel"}</button></div>
    {jobId && <div className="mt-4"><JobProgress job={job} />{job?.status === "SUCCEEDED" && job.result?.export_id && <button type="button" className="btn btn-outline btn-sm mt-2" disabled={busy} onClick={download}>下载 {job.result.file_name || "报表"}</button>}</div>}
    {(error || jobError) && <p role="alert" className="mt-2 text-sm text-error">{error || jobError.message}</p>}
  </div>
}
