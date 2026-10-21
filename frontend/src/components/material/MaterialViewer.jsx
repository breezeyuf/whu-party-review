import { useEffect, useMemo, useState } from "react"
import { materialPage } from "../../api/materials"
import { useBlobUrl } from "../../hooks/useBlobUrl"
import { Loading } from "../common/States"

export default function MaterialViewer({ materialId, versionId, page, onPage, highlights = [], activeId }) {
  const [scale, setScale] = useState(1.2)
  const [pageNo, setPageNo] = useState(page || 1)
  const [previewAttempt, setPreviewAttempt] = useState(0)
  const [imageError, setImageError] = useState(false)

  useEffect(() => { if (page) setPageNo(page) }, [page])
  useEffect(() => { setImageError(false) }, [materialId, versionId, pageNo, scale])

  const { url, meta, loading, error } = useBlobUrl(
    () => materialPage(materialId, pageNo, { version_id: versionId, scale }),
    [materialId, versionId, pageNo, scale, previewAttempt],
  )

  const boxes = useMemo(() => {
    return (highlights || []).filter((h) => Number(h.page_no) === Number(pageNo) && h.bbox)
  }, [highlights, pageNo])

  const pageCount = meta?.pageCount || 1
  const pw = meta?.pageWidth || 595
  const ph = meta?.pageHeight || 842

  const go = (n) => {
    const next = Math.min(Math.max(1, n), pageCount)
    setPageNo(next)
    onPage?.(next)
  }

  if (!materialId) return <p className="text-sm text-base-content/50">选择一份材料以预览。</p>

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
        <button type="button" className="btn btn-xs" disabled={pageNo <= 1} onClick={() => go(pageNo - 1)}>上一页</button>
        <span className="mono">第 {pageNo} / {pageCount} 页</span>
        <button type="button" className="btn btn-xs" disabled={pageNo >= pageCount} onClick={() => go(pageNo + 1)}>下一页</button>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setScale((s) => Math.max(0.6, +(s - 0.2).toFixed(1)))}>缩小</button>
        <span className="mono">{Math.round(scale * 100)}%</span>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setScale((s) => Math.min(2.4, +(s + 0.2).toFixed(1)))}>放大</button>
      </div>
      {loading && <Loading label="渲染页面" />}
      {(error || imageError) && (
        <div className="alert alert-error mb-2 py-2 text-xs" role="alert">
          <span>{imageError ? "材料预览图片无法显示。" : `材料预览失败：${error.message || "请稍后重试"}`}</span>
          <button type="button" className="btn btn-xs" disabled={loading} onClick={() => { setImageError(false); setPreviewAttempt((n) => n + 1) }}>重试</button>
        </div>
      )}
      {url && !imageError && (
        <div className="relative inline-block max-w-full overflow-auto rounded border border-base-300 bg-base-200">
          <img src={url} alt={`第 ${pageNo} 页`} className="block max-w-full" onError={() => setImageError(true)} />
          <div className="pointer-events-none absolute inset-0">
            {boxes.map((h) => {
              const [x1, y1, x2, y2] = h.bbox
              const style = {
                left: `${(x1 / pw) * 100}%`,
                top: `${(y1 / ph) * 100}%`,
                width: `${((x2 - x1) / pw) * 100}%`,
                height: `${((y2 - y1) / ph) * 100}%`,
              }
              const active = activeId && String(activeId) === String(h.id)
              return (
                <div
                  key={h.id || `${x1}-${y1}`}
                  className={`absolute border-2 ${active ? "border-error bg-error/20" : "border-warning bg-warning/15"}`}
                  style={style}
                  title={h.title || ""}
                />
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
