import { useState } from "react"
import JobProgress from "../../components/common/JobProgress"
import { useJobPolling } from "../../hooks/useJobPolling"

function TaskMonitor({ jobId, onDone, onRetry }) {
  const { job, error } = useJobPolling(jobId, { onDone })
  return (
    <div className="space-y-2">
      {!job && !error && <p className="text-sm text-base-content/60">正在读取任务 #{jobId}…</p>}
      {error && <div className="alert alert-warning text-sm">任务进度暂不可用：{error.message}。正在自动重连。</div>}
      <JobProgress job={job} onRetry={onRetry} />
    </div>
  )
}

// A failed task may be retried under the same id. Remount its monitor so a
// previously completed polling loop starts again after the retry succeeds.
export default function StudentTaskProgress({ jobId, onDone, onRestart }) {
  const [attempt, setAttempt] = useState(0)
  if (!jobId) return null
  return <TaskMonitor key={`${jobId}-${attempt}`} jobId={jobId} onDone={onDone} onRetry={() => { onRestart?.(); setAttempt((value) => value + 1) }} />
}
