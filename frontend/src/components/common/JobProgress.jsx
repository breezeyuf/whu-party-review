import { retryJob } from "../../api/jobs"
import { useState } from "react"
import { useMeta } from "../../context/MetaContext"
import { statusName } from "../../utils/format"

const JOB_TYPE_NAME = {
  PARSE: "材料解析",
  AI_CHECK: "AI 校验",
  BATCH_AI_CHECK: "批量 AI 校验",
  BATCH_UPLOAD: "批量上传",
  EXPORT: "数据导出",
}
const JOB_STATUS_NAME = { QUEUED: "排队中", RUNNING: "运行中", SUCCEEDED: "已完成", PARTIAL: "部分失败", FAILED: "失败" }

export default function JobProgress({ job, onRetry }) {
  const [busy, setBusy] = useState(false)
  const [retryError, setRetryError] = useState("")
  const meta = useMeta()
  if (!job) return null
  const total = job.total || 0
  const done = (job.done_count || 0) + (job.failed_count || 0)
  const pct = job.progress != null ? job.progress : (total ? Math.round((done / total) * 100) : (job.status === "SUCCEEDED" ? 100 : 8))
  const failed = job.status === "FAILED" || job.status === "PARTIAL"

  // 重试接口只在这里调用一次；失败时就地显示原因，成功后再通知页面刷新
  const retry = async () => {
    setBusy(true)
    setRetryError("")
    try {
      await retryJob(job.id)
    } catch (error) {
      setRetryError(error.message || "重试失败，请稍后再试")
      setBusy(false)
      return
    }
    setBusy(false)
    onRetry?.()
  }

  return (
    <div className="surface-card p-3">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span>{job.stage_text || JOB_TYPE_NAME[job.job_type] || "任务"} · {JOB_STATUS_NAME[job.status] || statusName(meta, job.status)}</span>
        <span className="mono">{total ? `${done}/${total}` : `${pct}%`}</span>
      </div>
      <progress className={`progress w-full ${failed ? "progress-error" : "progress-primary"}`} value={pct} max="100" />
      {job.error && <p className="mt-2 text-xs text-error">{job.error}</p>}
      {failed && (
        <button type="button" className="btn btn-outline btn-xs mt-2" disabled={busy} onClick={retry}>{busy ? "重试中…" : "重试"}</button>
      )}
      {retryError && <p role="alert" className="mt-2 text-xs text-error">{retryError}</p>}
    </div>
  )
}
