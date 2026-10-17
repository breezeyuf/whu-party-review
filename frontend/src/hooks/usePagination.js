import { useCallback, useMemo, useRef } from "react"
import { useSearchParams } from "react-router-dom"

export function usePagination(defaults = {}) {
  const [params, setParams] = useSearchParams()
  const defaultsRef = useRef(defaults)

  const query = useMemo(() => {
    const out = { page: 1, page_size: 20, ...defaultsRef.current }
    params.forEach((value, key) => {
      if (value !== "") out[key] = key === "page" || key === "page_size" ? Number(value) : value
    })
    return out
  }, [params])

  const setQuery = useCallback((patch, { resetPage = true } = {}) => {
    const next = new URLSearchParams(params)
    Object.entries(patch).forEach(([k, v]) => {
      if (v == null || v === "") next.delete(k)
      else next.set(k, String(v))
    })
    if (resetPage && !("page" in patch)) next.set("page", "1")
    setParams(next, { replace: true })
  }, [params, setParams])

  const setPage = useCallback((page) => setQuery({ page }, { resetPage: false }), [setQuery])

  return { query, setQuery, setPage, params }
}
