import { useState } from "react"
import { Link } from "react-router-dom"
import { useJobPolling } from "../../hooks/useJobPolling"
import { retryJob } from "../../api/jobs"

const LABEL = { QUEUED: "排队中", RUNNING: "运行中", SUCCEEDED: "已完成", PARTIAL: "部分失败", FAILED: "失败", CANCELLED: "已取消" }

export default function ReviewJobStatus({ jobId, onDone, onRetry }) {
  const [attempt, setAttempt] = useState(0)
  if (!jobId) return null
  return <JobWatcher key={`${jobId}:${attempt}`} jobId={jobId} onDone={onDone} onRetry={() => { setAttempt((n) => n + 1); onRetry?.() }} />
}

function JobWatcher({ jobId, onDone, onRetry }) {
  const { job, error } = useJobPolling(jobId, { onDone })
  const [busy, setBusy] = useState(false)
  const [retryError, setRetryError] = useState("")
  const failed = ["FAILED", "PARTIAL"].includes(job?.status)
  const retry = async () => {
    setBusy(true)
    setRetryError("")
    try { await retryJob(jobId); onRetry() } catch (e) { setRetryError(e.message || "重试失败"); setBusy(false) }
  }
  const total = job?.total || 0
  // Worker done_count already includes failed children.
  const done = Math.min(total, job?.done_count || 0)
  const progress = job?.progress ?? (total ? Math.round(100 * done / total) : 0)
  return (
    <div className="surface-card space-y-2 p-3 text-xs" aria-live="polite">
      <div className="flex items-center justify-between gap-2">
        <span>AI 审核任务 #{jobId} · {job ? LABEL[job.status] || job.status : "加载中"}{job?.stage_text ? ` · ${job.stage_text}` : ""}</span>
        <span className="mono">{total ? `${done}/${total}` : `${progress}%`}{job?.failed_count ? ` · 失败 ${job.failed_count}` : ""}</span>
      </div>
      <progress className={`progress w-full ${failed ? "progress-error" : "progress-primary"}`} value={progress} max="100" />
      {error && <p className="text-error">任务状态获取失败：{error.message}。正在自动重试。</p>}
      {job?.error && <p className="text-error">{job.error}</p>}
      {!!job?.failed_children?.length && <ul className="space-y-1">{job.failed_children.map((child) => <li key={child.id}><Link className="link" to={`/review/submissions/${child.target_id}`}>提交包 #{child.target_id}</Link>：{child.error || "AI 检查失败"}</li>)}</ul>}
      {failed && <button type="button" className="btn btn-outline btn-xs" disabled={busy} onClick={retry}>{busy ? "重试中…" : "重试失败任务"}</button>}
      {retryError && <p className="text-error" role="alert">{retryError}</p>}
    </div>
  )
}
