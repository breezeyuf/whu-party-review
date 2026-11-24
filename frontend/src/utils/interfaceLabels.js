// Presentation labels only: API values and stored audit evidence remain intact.
const LABELS = {
 PENDING:"待处理", NEEDS_CONFIRM:"待确认类型", AUTO:"自动识别", CONFIRMED:"已确认", MODIFIED:"已修改确认", REJECTED:"已驳回",
 QUEUED:"排队中", RUNNING:"处理中", DONE:"已完成", SUCCEEDED:"已完成", FAILED:"失败", PARTIAL:"部分失败", CANCELLED:"已取消",
 DRAFT:"草稿", SENT:"已发送", ACTIVE:"进行中", COMPLETED:"已完成", CLOSED:"已关闭", SUSPENDED:"已暂停", DELETED:"已删除",
 OPEN:"待处理", UNRESOLVED:"复核后仍存在", RESOLVED:"已解决", WAIVED:"已豁免",
 RULE_ONLY:"仅规则检查", RULE_LLM:"规则与大模型检查", SELF_CHECK:"学生自查", REVIEW:"审核检查", RECHECK:"整改复核",
 MANUAL:"人工校正", RULE:"规则抽取", LLM:"大模型抽取", IMPORT:"导入记录", OCR:"图片文字识别", PDF_TEXT:"PDF文本提取", DOCX:"Word文本提取", MIXED:"文档文本与图片识别", NONE:"未启用", RAPIDOCR:"RapidOCR",
 REQUIRED:"待人工审核", NOT_REQUIRED:"无需人工接管", PASS:"通过", RETURN:"退回整改", FILE:"备案归档", SUBMIT:"提交审核", RESUBMIT:"整改重新提交",
 STUDENT:"学生", BRANCH_REVIEWER:"党支部审核员", CROSS_REVIEWER:"交叉互查审核员", COLLEGE_REVIEWER:"学院党委审核员", ORG_ADMIN:"组织部管理员", SYS_ADMIN:"系统管理员",
 BRANCH_REVIEW:"支部初审", CROSS_REVIEW:"交叉互查", COLLEGE_REVIEW:"学院复审", ORG_FILING:"组织部备案", FILED:"已备案",
}
export function uiLabel(value, fallback) {
 if (value == null || value === "") return fallback ?? "—"
 return LABELS[String(value).toUpperCase()] || fallback || String(value)
}
const REASONS = {
 LOW_CONFIDENCE:"自动检查结果需进一步核实",
 NEEDS_JUDGEMENT:"内容需要人工判断",
 KEY_STAGE:"本阶段须由人工确认",
 MATERIAL_CONFLICT:"不同材料的时间信息存在冲突",
}
export const handoverReasonLabel = code => REASONS[code] || "其他需人工核实的情况"

export function parsedWarning(warning) {
 const message = typeof warning === "string" ? warning : warning?.message || "识别结果需要核对"
 if (message.startsWith("视觉 OCR 未发送图片：尚未允许")) return {
   informational:true,
   message:"本次未进行视觉模型复核：未授权发送原图。这不表示本地识别失败，请核对下方识别文字。如需视觉复核，请由系统管理员检查授权配置。",
 }
 return {message,informational:false}
}
