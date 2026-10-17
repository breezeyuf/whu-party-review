import { useCallback, useEffect, useRef, useState } from "react"

export function useRequest(fn, deps = [], { immediate = true } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)
  const sequence = useRef(0)
  const alive = useRef(true)

  const run = useCallback(async (...args) => {
    const request = ++sequence.current
    setLoading(true)
    setError(null)
    try {
      const result = await fn(...args)
      if (alive.current && request === sequence.current) setData(result)
      return result
    } catch (e) {
      if (alive.current && request === sequence.current) setError(e)
      throw e
    } finally {
      if (alive.current && request === sequence.current) setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    alive.current = true
    setData(null)
    setError(null)
    if (immediate) run().catch(() => {})
    else setLoading(false)
    return () => { alive.current = false; sequence.current += 1 }
  }, [run, immediate])

  return { data, loading, error, setData, reload: run, run }
}
