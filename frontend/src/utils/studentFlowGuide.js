import { isAiPending, studentMaterials, pendingParseCount, pendingStudentReplies } from "./studentWorkflow.js"

export function studentFlowNotice(submission, { issues = [], groups = [], ready = true, taskPending = false } = {}) {
  if (!submission) return { title: "正在读取办理状态", description: "加载完成后显示下一步。" }
  if (submission.status === "FILED") return { title: "本阶段已完成备案", description: "可到发展进度查看后续安排。", to: "/my/progress", label: "查看发展进度" }
  if (!["DRAFT", "RETURNED"].includes(submission.status)) return { title: "已提交，等待审核", description: "当前无需重复提交；如被退回，整改中心会显示需要处理的问题。", to: "/my/progress", label: "查看审核进度" }
  if (taskPending || isAiPending(submission)) return { title: submission.status === "RETURNED" ? "正在复核整改材料" : "自查正在进行", description: "结果会自动刷新，请等待任务完成。" }
  if (!ready) return { title: "正在核对材料与回复状态", description: "请先完成加载；如显示失败，使用对应的重试按钮。" }
  const materials = studentMaterials(groups)
  const failed = materials.filter((m) => m.current_version?.parse_status === "FAILED")
  if (failed.length) return { title: `${failed.length} 份材料解析失败`, description: "解析失败不表示材料已通过。请检查原件、重试解析或上传清晰的新版本。", to: `/materials/${failed[0].id}`, label: "处理解析失败" }
  const parsing = pendingParseCount(groups)
  if (parsing) return { title: `${parsing} 份材料正在解析`, description: "完成后会自动刷新；请勿重复上传相同文件。" }
  const pending = pendingStudentReplies(submission, issues)
  if (pending.length) return { title: `还有 ${pending.length} 条问题待回复`, description: "对照原文修改材料并上传，或填写情况说明。回复保存后仍需审核人员复核。", to: "/my/rectification", label: "处理待回复问题" }
  if (!submission.can?.submit) return { title: "当前仅可查看", description: "可查看材料和报告；办理权限以当前身份和提交状态为准。" }
  if (submission.status === "RETURNED") return { title: "待回复问题已处理", description: "可点击“重新提交”，系统将自动复核。回复已保存不等于问题已通过审核。" }
  const report = submission.latest_report
  if (!report || report.is_stale || (report.status && report.status !== "DONE") || submission.ai_status === "FAILED") return { title: report?.is_stale ? "材料已更新，需要重新自查" : "下一步：发起自查", description: "生成当前材料的检查报告后，再处理报告中的问题并提交审核。" }
  return { title: "自查已完成，可提交审核", description: "请核对报告与材料；提交后将进入人工审核，不代表已经审核通过。" }
}

export function studentMaterialReturn(submissionId, searchParams) {
  const number = Number(submissionId)
  if (!Number.isSafeInteger(number) || number <= 0) return { to: "/my/materials", label: "返回我的材料" }
  if (searchParams.get("from") === "self-check") {
    const report = Number(searchParams.get("report"))
    return { to: `/my/self-check/${number}${Number.isSafeInteger(report) && report > 0 ? `?report=${report}` : ""}`, label: "返回自查报告" }
  }
  if (searchParams.get("from") === "rectification") {
    const issue = Number(searchParams.get("issue_id"))
    return { to: `/my/rectification${Number.isSafeInteger(issue) && issue > 0 ? `?issue_id=${issue}` : ""}`, label: "返回整改回复" }
  }
  return { to: "/my/materials", label: "返回我的材料" }
}
