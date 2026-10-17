import { useEffect, useState } from "react"

export function useBlobUrl(loader, deps = []) {
  const [url, setUrl] = useState("")
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    let objectUrl = ""
    setLoading(true)
    setError(null)
    setUrl("")
    loader().then(({ blob, headers, filename }) => {
      if (!alive) return
      objectUrl = URL.createObjectURL(blob)
      setUrl(objectUrl)
      setMeta({
        filename,
        pageCount: Number(headers?.["x-page-count"] || 0) || undefined,
        pageWidth: Number(headers?.["x-page-width"] || 0) || undefined,
        pageHeight: Number(headers?.["x-page-height"] || 0) || undefined,
      })
    }).catch((e) => { if (alive) setError(e) })
      .finally(() => { if (alive) setLoading(false) })
    return () => {
      alive = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { url, meta, loading, error }
}
