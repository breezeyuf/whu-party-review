import { useEffect, useState } from "react"
import { compareOcrText } from "../../utils/ocrReview"
import MaterialViewer from "./MaterialViewer"

export default function OcrReviewSuggestions({ parsed, editable, busy, onApply }) {
  const [reviewSource, setReviewSource] = useState(null)
  const [acknowledged, setAcknowledged] = useState({})
  useEffect(() => { setReviewSource(null); setAcknowledged({}) }, [parsed])
  if (!(parsed.pages || []).some((page) => page.vision_reviews?.length)) return null
  return (
<section className="space-y-2 rounded border border-base-300 p-3" aria-label="视觉 OCR 复核结果">
        <h3 className="text-sm font-medium">视觉 OCR 复核建议</h3>
        <p className="text-xs text-base-content/60">以下为模型原始建议记录，不代表已采纳。请对照对应页原图，尤其核对姓名和日期；填入后仍须保存校正。已保存的校正以解析文本为准。</p>
        {reviewSource && <div className="rounded border border-base-300 p-2">
          <button type="button" className="btn btn-ghost btn-xs mb-2" onClick={() => setReviewSource(null)}>收起复核原图</button>
          <MaterialViewer materialId={parsed.material_id} versionId={parsed.version_id} page={reviewSource.page_no} pageCount={parsed.page_count} highlights={[reviewSource]} activeId="ocr-review" />
        </div>}
        {(parsed.pages || []).flatMap((page) => (page.vision_reviews || []).map((review, index) => { const comparison = compareOcrText(review.original_text || "", review.candidate_text || ""); const reviewKey = `${page.page_no}-${index}`; return <div key={reviewKey} className="space-y-1 border-t border-base-300 pt-2 text-xs">
          <p>第 {page.page_no} 页 · {review.block_index == null ? "整页" : `文字块 ${review.block_index + 1}`} · {review.model} · {review.status === "failed" ? "复核失败" : review.status === "unchanged" ? "与本地结果一致" : "需人工核对"}</p>
          {parsed.material_id && <button type="button" className="btn btn-ghost btn-xs" onClick={() => setReviewSource({ id: "ocr-review", page_no: page.page_no, bbox: review.bbox, version_id: parsed.version_id, title: "视觉 OCR 复核区域" })}>查看原图区域</button>}
          {review.error ? <p className="text-warning">{review.error}</p> : <>
            <div className="grid gap-3 lg:grid-cols-2">
              <div className="min-w-0 rounded-lg border border-base-300 bg-base-200/40 p-3"><h4 className="mb-2 font-medium">本地 OCR 原文 · {comparison.beforeCount} 字符</h4><p className="max-h-64 overflow-auto whitespace-pre-wrap break-words leading-relaxed">{comparison.prefix}<mark className="bg-error/10 text-base-content">{comparison.removed}</mark>{comparison.suffix}{!review.original_text && "（未识别到文字）"}</p></div>
              <div className="min-w-0 rounded-lg border border-primary/20 bg-primary/5 p-3"><h4 className="mb-2 font-medium">模型建议 · {comparison.afterCount} 字符</h4><p className="max-h-64 overflow-auto whitespace-pre-wrap break-words leading-relaxed">{comparison.prefix}<mark className="bg-success/15 text-base-content">{comparison.added}</mark>{comparison.suffix}{!review.candidate_text && "（空白）"}</p></div>
            </div>
            <p className="text-base-content/60">{review.confidence_provided === false || review.confidence == null || (review.confidence_provided == null && review.confidence === 0) ? "模型未提供置信度，不代表识别正确率为 0%。" : `模型自报置信度：${Math.round(review.confidence * 100)}%（仅供参考）`}{review.uncertain ? " · 建议仍需人工核对" : ""}</p>
            {comparison.warnings.length > 0 && <div className="rounded-lg border border-warning/30 bg-warning/5 p-2" role="note">{comparison.warnings.map((warning) => <p key={warning}>{warning}</p>)}{editable && review.status === "pending" && <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={!!acknowledged[reviewKey]} onChange={(e) => setAcknowledged((values) => ({ ...values, [reviewKey]: e.target.checked }))} />我已对照原图核对上述变化</label>}</div>}
            {editable && review.status === "pending" && <button type="button" className="btn btn-outline btn-sm" disabled={busy || (comparison.warnings.length > 0 && !acknowledged[reviewKey])} onClick={() => {
              onApply(page, review)
            }}>核对后填入校正文本</button>}
          </>}
        </div> }))}
      </section>
  )
}
