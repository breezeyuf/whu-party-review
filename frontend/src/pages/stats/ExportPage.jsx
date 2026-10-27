import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import JobProgress from "../../components/common/JobProgress"
import { useJobPolling } from "../../hooks/useJobPolling"
import { downloadExport, exportStats } from "../../api/stats"
import { listBatches } from "../../api/batches"
import { saveBlob } from "../../api/client"
import { useRequest } from "../../hooks/useRequest"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"

export default function ExportPage() {
  const toast = useToast()
  const meta = useMeta()
  const [form, setForm] = useState({ export_type: "STATS_REPORT", batch_id: "", stage_code: "", date_from: "", date_to: "" })
  const [jobId, setJobId] = useState(null)
  const [pollRestart, setPollRestart] = useState(0)
  const [starting, setStarting] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const batches = useRequest(() => listBatches({ page_size: 200 }), [])
  const { job, error: jobError } = useJobPolling(jobId, { restartKey: pollRestart })
  const jobBusy = ["QUEUED", "RUNNING"].includes(job?.status)

  const start = async () => {
    if (starting || jobBusy) return
    if (form.date_from && form.date_to && form.date_from > form.date_to) {
      toast.error("结束日期不能早于开始日期")
      return
    }
    const filters = {}
    ;["batch_id", "stage_code", "date_from", "date_to"].forEach((k) => { if (form[k]) filters[k] = form[k] })
    setStarting(true)
    try {
      const res = await exportStats({ export_type: form.export_type, filters })
      setJobId(res.job_id)
      toast.info("导出任务已排队")
    } catch (e) {
      toast.error(e.message || "导出任务创建失败")
    } finally {
      setStarting(false)
    }
  }

  const download = async () => {
    const id = job?.result?.export_id
    if (!id || downloading) return
    setDownloading(true)
    try {
      saveBlob(await downloadExport(id))
    } catch (e) {
      toast.error(e.message || "下载失败，请稍后重试")
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="max-w-xl">
      <PageHeader title="报表导出">
        去隐私导出会去掉姓名、学号、证件和联系方式，或替换为匿名编号。导出记入审计日志。
      </PageHeader>
      <div className="surface-card space-y-3 p-4">
        <label className="form-control">
          <span className="label-text text-xs">类型</span>
          <select className="select select-bordered select-sm" value={form.export_type} onChange={(e) => setForm({ ...form, export_type: e.target.value })}>
            <option value="STATS_REPORT">统计报表</option>
            <option value="DESENSITIZED_DATA">去隐私审核数据</option>
            <option value="AI_QUALITY">AI 效能</option>
          </select>
        </label>
        <label className="form-control">
          <span className="label-text text-xs">发展批次</span>
          <select className="select select-bordered select-sm" value={form.batch_id} onChange={(e) => setForm({ ...form, batch_id: e.target.value })} disabled={batches.loading || !!batches.error}>
            <option value="">全部批次</option>
            {(batches.data?.items || []).map((batch) => <option key={batch.id} value={batch.id}>{batch.name}（{batch.year}）</option>)}
          </select>
          {batches.error && <span className="flex flex-wrap items-center gap-2 text-xs text-error">批次列表加载失败。<button type="button" className="btn btn-ghost btn-xs" onClick={() => batches.reload().catch(() => {})}>重试</button></span>}
        </label>
        <label className="form-control">
          <span className="label-text text-xs">发展阶段</span>
          <select className="select select-bordered select-sm" value={form.stage_code} onChange={(e) => setForm({ ...form, stage_code: e.target.value })}>
            <option value="">全部阶段</option>
            {(meta.stages || []).map((stage) => <option key={stage.code} value={stage.code}>{stage.name}</option>)}
          </select>
        </label>
        <div className="grid grid-cols-2 gap-2">
          <label className="form-control"><span className="label-text text-xs">开始日期</span><input type="date" className="input input-bordered input-sm" value={form.date_from} onChange={(e) => setForm({ ...form, date_from: e.target.value })} /></label>
          <label className="form-control"><span className="label-text text-xs">结束日期</span><input type="date" className="input input-bordered input-sm" value={form.date_to} onChange={(e) => setForm({ ...form, date_to: e.target.value })} /></label>
        </div>
        <button type="button" className="btn btn-primary btn-sm" disabled={starting || batches.loading || jobBusy || !!batches.error} onClick={start}>{starting ? "创建任务中…" : jobBusy ? "导出处理中…" : "生成 Excel"}</button>
      </div>
      {jobId && (
        <div className="mt-4 space-y-2">
          {jobError && <p className="text-sm text-error" role="alert">任务状态暂时无法更新：{jobError.message || "网络错误"}。系统会继续尝试查询。</p>}
          <JobProgress job={job} onRetry={() => setPollRestart((value) => value + 1)} />
          {job?.result?.download_url && <button type="button" className="btn btn-outline btn-sm" disabled={downloading} onClick={download}>{downloading ? "下载中…" : `下载 ${job.result.file_name || "报表"}`}</button>}
        </div>
      )}
    </div>
  )
}
