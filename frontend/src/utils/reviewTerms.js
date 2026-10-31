export const severityCode = code => ["阻断", "关键问题"].includes(code) ? "BLOCK" : code
export const displaySeverities = rows => (rows || []).map(row => row.code === "BLOCK" ? { ...row, name: "关键问题" } : row)
const LEGACY_MESSAGES = {
  "存在未回复的阻断问题": "存在未回复的关键问题",
  "仍有未处理的阻断问题": "仍有未处理的关键问题",
}
export const reviewMessage = message => LEGACY_MESSAGES[message] || message
