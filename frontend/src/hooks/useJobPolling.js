import { useEffect, useRef, useState } from "react"
import { getJob } from "../api/jobs"

const DONE = new Set(["SUCCEEDED", "FAILED", "PARTIAL", "CANCELLED"])

export function useJobPolling(jobId, { interval = 1500, onDone, restartKey = 0 } = {}) {
  const [result, setResult] = useState(null)
  const current = result?.jobId === jobId && result?.restartKey === restartKey ? result : null
  const doneRef = useRef(onDone)

  useEffect(() => {
    doneRef.current = onDone
  }, [onDone])

  useEffect(() => {
    if (!jobId) { setResult(null); return undefined }
    let alive = true
    let timer = null
    const tick = async () => {
      try {
        const data = await getJob(jobId)
        if (!alive) return
        setResult({ jobId, restartKey, job: data, error: null })
        if (DONE.has(data.status)) {
          doneRef.current?.(data)
          return
        }
      } catch (e) {
        if (!alive) return
        setResult(previous => ({
          jobId, restartKey, error: e,
          job: previous?.jobId === jobId && previous.restartKey === restartKey ? previous.job : null,
        }))
      }
      timer = setTimeout(tick, interval)
    }
    tick()
    return () => {
      alive = false
      if (timer) clearTimeout(timer)
    }
  }, [jobId, interval, restartKey])

  const job = current?.job ?? null
  return { job, error: current?.error ?? null, pending: !!jobId && !DONE.has(job?.status) }
}
