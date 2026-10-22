import { useEffect, useMemo, useRef, useState } from "react"
import { materialPage } from "../../api/materials"
import { useBlobUrl } from "../../hooks/useBlobUrl"
import { Loading } from "../common/States"
import { positiveInteger, validBbox } from "../../utils/materialWorkflow"
import { pagePoint, regionBox } from "../../utils/regionSelection"

export default function MaterialViewer({ materialId, versionId, page, onPage, pageCount: knownPageCount, highlights = [], activeId, refreshKey, onSelectRegion }) {
  const [scale, setScale] = useState(1.2)
  const [pageNo, setPageNo] = useState(positiveInteger(page) || 1)
  const [retryKey, setRetryKey] = useState(0)
  const [selecting, setSelecting] = useState(false)
  const [selection, setSelection] = useState(null)
  const drag = useRef(null)

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

  useEffect(() => {
    drag.current = null
    setSelection(null)
    setSelecting(false)
  }, [materialId, versionId, requestedPage, scale, refreshKey, onSelectRegion === undefined])

  useEffect(() => {
    if (!selecting) return undefined
    const escape = (event) => { if (event.key === "Escape") { drag.current = null; setSelection(null); setSelecting(false) } }
    window.addEventListener("keydown", escape)
    return () => window.removeEventListener("keydown", escape)
  }, [selecting])

  const cancelSelection = () => { drag.current = null; setSelection(null); setSelecting(false) }
  const point = (event) => pagePoint(event.clientX, event.clientY, event.currentTarget.getBoundingClientRect(), pw, ph)
  const startSelection = (event) => {
    if (!selecting || loading || error || (event.button != null && event.button !== 0)) return
    const start = point(event)
    if (!start) return
    event.preventDefault()
    drag.current = { start, pointerId: event.pointerId }
    setSelection(null)
    event.currentTarget.setPointerCapture?.(event.pointerId)
  }
  const moveSelection = (event) => {
    if (!drag.current || drag.current.pointerId !== event.pointerId) return
    const end = point(event)
    if (end) setSelection(regionBox(drag.current.start, end))
  }
  const finishSelection = (event) => {
    if (!drag.current || drag.current.pointerId !== event.pointerId) return
    const start = drag.current.start
    drag.current = null
    event.currentTarget.releasePointerCapture?.(event.pointerId)
    const end = point(event)
    if (!end) return
    const rect = event.currentTarget.getBoundingClientRect()
    const bbox = regionBox(start, end)
    if ((bbox[2] - bbox[0]) / pw * rect.width < 4 || (bbox[3] - bbox[1]) / ph * rect.height < 4) { setSelection(null); return }
    setSelection(bbox)
    setSelecting(false)
    onSelectRegion?.({ material_id: materialId, version_id: versionId, page_no: requestedPage, bbox })
  }

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
        {onSelectRegion && <button type="button" className={`btn btn-xs ${selecting ? "btn-primary" : "btn-outline"}`} disabled={loading || !!error || !url} aria-pressed={selecting} onClick={() => selecting ? cancelSelection() : (setSelection(null), setSelecting(true))}>{selecting ? "取消框选" : "框选新增问题"}</button>}
      </div>
      {selecting && <p role="status" className="mb-2 text-xs text-primary">在原文上按住并拖动框选问题区域，松开后填写问题。按 Esc 取消。</p>}
      {loading && <Loading label="渲染页面" />}
      {error && <p role="alert" className="text-xs text-error">{error.message} <button type="button" className="link" onClick={() => setRetryKey((key) => key + 1)}>重新加载预览</button></p>}
      {url && (
        <div className="inline-block max-w-full overflow-auto rounded border border-base-300 bg-base-200">
          <div className="relative" role={selecting ? "region" : undefined} aria-label={selecting ? "框选问题区域" : undefined} tabIndex={selecting ? 0 : undefined}
            style={selecting ? { cursor: "crosshair", touchAction: "none", userSelect: "none" } : undefined}
            onPointerDown={startSelection} onPointerMove={moveSelection} onPointerUp={finishSelection}
            onPointerCancel={() => { drag.current = null; setSelection(null) }}
            onKeyDown={(event) => { if (event.key === "Escape") cancelSelection() }}>
          <img src={url} alt={`第 ${requestedPage} 页`} className="block max-w-full" draggable={false} />
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
            {selection && <div aria-label="已框选区域" className="absolute border-2 border-dashed border-primary bg-primary/15" style={{ left: `${selection[0] / pw * 100}%`, top: `${selection[1] / ph * 100}%`, width: `${(selection[2] - selection[0]) / pw * 100}%`, height: `${(selection[3] - selection[1]) / ph * 100}%` }} />}
          </div>
          </div>
        </div>
      )}
    </div>
  )
}
