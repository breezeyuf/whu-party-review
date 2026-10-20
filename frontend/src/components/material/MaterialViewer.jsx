import { useEffect, useMemo, useState } from "react"
import { materialPage } from "../../api/materials"
import { useBlobUrl } from "../../hooks/useBlobUrl"
import { Loading } from "../common/States"
import { positiveInteger, validBbox } from "../../utils/materialWorkflow"

export default function MaterialViewer({ materialId, versionId, page, onPage, pageCount: knownPageCount, highlights = [], activeId, refreshKey }) {
  const [scale, setScale] = useState(1.2)
  const [pageNo, setPageNo] = useState(positiveInteger(page) || 1)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => { setPageNo(positiveInteger(page) || 1) }, [materialId, versionId, page])
  const requestedPage = Math.min(pageNo, positiveInteger(knownPageCount) || pageNo)

  const { url, meta, loading, error } = useBlobUrl(
    () => materialId ? materialPage(materialId, requestedPage, { version_id: versionId, scale }) : Promise.reject(new Error("请选择材料")),
    [materialId, versionId, requestedPage, scale, refreshKey, retryKey],
  )

  const boxes = useMemo(() => {
    return (highlights || []).filter((h) => Number(h.page_no) === Number(requestedPage) && validBbox(h.bbox)
      && (!h.version_id || !versionId || String(h.version_id) === String(versionId))
      && (!h.material_version_id || !versionId || String(h.material_version_id) === String(versionId)))
  }, [highlights, requestedPage, versionId])

  const pageCount = positiveInteger(knownPageCount) || (url ? meta?.pageCount : null) || requestedPage
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
        <button type="button" className="btn btn-xs" disabled={loading || requestedPage <= 1} onClick={() => go(requestedPage - 1)}>上一页</button>
        <span className="mono">第 {requestedPage} / {pageCount} 页</span>
        <button type="button" className="btn btn-xs" disabled={loading || requestedPage >= pageCount} onClick={() => go(requestedPage + 1)}>下一页</button>
        <label className="flex items-center gap-1">跳至<input aria-label="跳转预览页码" type="number" min="1" max={pageCount} className="input input-bordered input-xs w-16" value={requestedPage} disabled={loading} onChange={(event) => { const next = positiveInteger(event.target.value); if (next) go(next) }} />页</label>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setScale((s) => Math.max(0.6, +(s - 0.2).toFixed(1)))}>缩小</button>
        <span className="mono">{Math.round(scale * 100)}%</span>
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => setScale((s) => Math.min(2.4, +(s + 0.2).toFixed(1)))}>放大</button>
      </div>
      {loading && <Loading label="渲染页面" />}
      {error && <p role="alert" className="text-xs text-error">{error.message} <button type="button" className="link" onClick={() => setRetryKey((key) => key + 1)}>重新加载预览</button></p>}
      {url && (
        <div className="relative inline-block max-w-full overflow-auto rounded border border-base-300 bg-base-200">
          <img src={url} alt={`第 ${requestedPage} 页`} className="block max-w-full" />
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
                  key={h.id ?? `${x1}-${y1}`}
                  className={`absolute border-2 ${active ? "border-error bg-error/20" : "border-warning bg-warning/15"}`}
                  style={style}
                  title={h.title || ""}
                  aria-label={h.title || "问题位置"}
                />
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
