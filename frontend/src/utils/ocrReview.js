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


// These checks flag review risks; they do not judge which transcription is correct.
export function compareOcrText(original = "", candidate = "") {
  const before = Array.from(original), after = Array.from(candidate)
  let prefix = 0, suffix = 0
  while (prefix < before.length && prefix < after.length && before[prefix] === after[prefix]) prefix++
  while (suffix < before.length - prefix && suffix < after.length - prefix && before[before.length - 1 - suffix] === after[after.length - 1 - suffix]) suffix++
  const normalize = (value) => value.normalize("NFKC").replace(/\s/g, "")
  const a = normalize(original), b = normalize(candidate)
  const warnings = []
  if (a.length >= 20 && b.length < a.length * 0.75) warnings.push("建议文字明显变短，可能漏字；也可能移除了划掉内容，请逐行对照原图。")
  if (JSON.stringify(a.match(/\d+/g) || []) !== JSON.stringify(b.match(/\d+/g) || [])) warnings.push("数字有变化，请重点核对日期、编号和数量。")
  return { prefix: before.slice(0, prefix).join(""), removed: before.slice(prefix, before.length - suffix).join(""), added: after.slice(prefix, after.length - suffix).join(""), suffix: suffix ? before.slice(-suffix).join("") : "", warnings, beforeCount: a.length, afterCount: b.length }
}
