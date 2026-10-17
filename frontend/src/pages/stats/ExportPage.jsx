import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import JobProgress from "../../components/common/JobProgress"
import { useJobPolling } from "../../hooks/useJobPolling"
import { downloadExport, exportStats } from "../../api/stats"
import { saveBlob } from "../../api/client"
import { useToast } from "../../context/ToastContext"

export default function ExportPage() {
  const toast = useToast()
  const [form, setForm] = useState({ export_type: "STATS_REPORT", batch_id: "", stage_code: "", date_from: "", date_to: "" })
  const [jobId, setJobId] = useState(null)
  const { job } = useJobPolling(jobId)

  const start = async () => {
    const filters = {}
    ;["batch_id", "stage_code", "date_from", "date_to"].forEach((k) => { if (form[k]) filters[k] = form[k] })
    const res = await exportStats({ export_type: form.export_type, filters })
    setJobId(res.job_id)
    toast.info("导出任务已排队")
  }

  const download = async () => {
    const id = job?.result?.export_id
    if (!id) return
    saveBlob(await downloadExport(id))
  }

  return (
    <div className="max-w-xl">
      <PageHeader title="数据导出">
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
          <span className="label-text text-xs">批次 ID</span>
          <input className="input input-bordered input-sm" value={form.batch_id} onChange={(e) => setForm({ ...form, batch_id: e.target.value })} />
        </label>
        <div className="grid grid-cols-2 gap-2">
          <input className="input input-bordered input-sm" placeholder="开始日期" value={form.date_from} onChange={(e) => setForm({ ...form, date_from: e.target.value })} />
          <input className="input input-bordered input-sm" placeholder="结束日期" value={form.date_to} onChange={(e) => setForm({ ...form, date_to: e.target.value })} />
        </div>
        <button type="button" className="btn btn-primary btn-sm" onClick={start}>生成 Excel</button>
      </div>
      {jobId && (
        <div className="mt-4 space-y-2">
          <JobProgress job={job} />
          {job?.result?.download_url && <button type="button" className="btn btn-outline btn-sm" onClick={download}>下载 {job.result.file_name || "报表"}</button>}
        </div>
      )}
    </div>
  )
}
