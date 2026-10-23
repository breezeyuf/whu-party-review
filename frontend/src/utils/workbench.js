export function nextStudentAction(submission = {}, progress) {
  if (submission.status === "RETURNED") return { title: "处理退回的问题", description: "按审核意见补充材料、填写回复，再重新提交。", label: "去整改", to: "/my/rectification", step: 1 }
  if (submission.status === "FILED") return { title: "本阶段已完成", description: "材料已备案，可查看发展进度与审核记录。", label: "查看发展进度", to: "/my/progress", step: 3 }
  if (submission.status && submission.status !== "DRAFT") return { title: "材料正在审核", description: "当前无需重复提交。审核结果会通过消息通知你。", label: "查看审核进度", to: "/my/progress", step: 2 }
  if (!submission.id || !progress || progress.actual < progress.expected || progress.expected === 0) return { title: "准备本阶段材料", description: "按清单上传材料。缺少的材料会在页面中标出。", label: "去准备材料", to: "/my/materials", step: 0 }
  return { title: "完成自查并提交", description: "材料已按清单准备好。检查问题与修改建议后，提交审核。", label: "去自查并提交", to: `/my/self-check/${submission.id}`, step: 1 }
}

export function isMenuActive(pathname, destination) {
  if (destination === "/review/tasks" && pathname.startsWith("/review/submissions/")) return true
  return destination === "/" ? ["/", "/student", "/review", "/admin"].includes(pathname) : pathname === destination || pathname.startsWith(`${destination}/`)
}

export function countActiveFilters(values, keys) {
  return keys.filter((key) => values[key] != null && values[key] !== "").length
}
