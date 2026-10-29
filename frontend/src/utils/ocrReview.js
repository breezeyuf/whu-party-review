export function pendingOcrPages(parsed) {
  return (parsed?.pages || []).filter((page) => page.ocr_status === "NEEDS_REVIEW"
    || page.ocr_status == null && ["scan", "image", "ocr"].includes(page.source) && !(page.text || "").trim())
}

// Only edit a unique, still-unmodified source span. Never overwrite user edits.
export function applyOcrSuggestion(text, parsed, page, review) {
  const original = review.original_text || ""
  const candidate = review.candidate_text
  if (review.status !== "pending" || typeof candidate !== "string") throw new Error("没有可填入的复核建议")
  if (original) {
    const at = text.indexOf(original)
    if (at < 0 || text.indexOf(original, at + 1) >= 0) throw new Error("原文已修改或有重复，请对照原图手动修改解析文本")
    return text.slice(0, at) + candidate + text.slice(at + original.length)
  }
  const pages = parsed.pages || []
  if (review.block_index == null && text === parsed.full_text && pages.map((p) => p.text || "").join("\n") === text) {
    return pages.map((p) => p.page_no === page.page_no ? candidate : (p.text || "")).join("\n")
  }
  throw new Error("无法定位空白原文，请对照原图手动填写解析文本")
}
