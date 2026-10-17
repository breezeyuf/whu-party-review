import { useEffect, useRef, useState } from "react"
import { getJob } from "../api/jobs"

const DONE = new Set(["SUCCEEDED", "FAILED", "PARTIAL", "CANCELLED"])

export function useJobPolling(jobId, { interval = 1500, onDone } = {}) {
  const [job, setJob] = useState(null)
  const [error, setError] = useState(null)
  const doneRef = useRef(onDone)

  useEffect(() => {
    doneRef.current = onDone
  }, [onDone])

  useEffect(() => {
    if (!jobId) {
      setJob(null)
      setError(null)
      return undefined
    }
    let alive = true
    let timer = null
    const tick = async () => {
      try {
        const data = await getJob(jobId)
        if (!alive) return
        setJob(data)
        setError(null)
        if (DONE.has(data.status)) {
          doneRef.current?.(data)
          return
        }
      } catch (e) {
        if (!alive) return
        setError(e)
      }
      timer = setTimeout(tick, interval)
    }
    tick()
    return () => {
      alive = false
      if (timer) clearTimeout(timer)
    }
  }, [jobId, interval])

  return { job, error }
}
