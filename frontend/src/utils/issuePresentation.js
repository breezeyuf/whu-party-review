// Explain system-generated findings without rewriting stored reports or originals.
export function issuePresentation(issue, definitions = []) {
  if (issue.source === "MANUAL") return issue
  const names = { T01: "出生日期", T02: "递交入党申请书日期", ...Object.fromEntries(definitions.map(n => [n.code, n.name])) }
  const label = text => String(text || "").replace(/\bT\d{2}\b/g, code => names[code] || code).replace(/《\s*》/g, "本次提交材料")
  const missing = `${issue.description || ""} ${issue.actual_value || ""}`
  if (issue.rule_code === "R-T22" && /缺少|缺失/.test(missing)) {
    const codes = [...new Set(missing.match(/\bT\d{2}\b/g) || [])]
    if (codes.length) return { ...issue,
      title: "本阶段必要日期尚未齐全",
      description: `系统尚未取得：${codes.map(code => names[code] || code).join("、")}。未识别到日期，不代表原件一定未填写。`,
      suggestion: "请先核对原件。原件中已有日期的，请由有权限的人员核对并补充或校正系统时间节点；原件确实缺少日期的，请按要求补充材料，再重新检查。",
    }
  }
  return { ...issue, description: label(issue.description), suggestion: label(issue.suggestion) }
}
