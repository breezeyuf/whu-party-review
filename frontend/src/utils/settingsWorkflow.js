import { validDate } from "./adminWorkflow.js"
export const SETTING_GROUPS = [
  ["ai", "大模型", true, [["llm_enabled","启用大模型","boolean"],["base_url","接口地址","text"],["model","模型名","text"],["timeout_s","超时秒数","number",1],["max_concurrency","最大并发","number",1],["temperature","温度","number",0,2],["desensitize","调用前脱敏","boolean"],["classify_confidence_threshold","分类置信度阈值","number",0,1]]],
  ["ocr","OCR",true,[["engine","引擎（auto、rapidocr 或 paddleocr）","text"],["timeout_s","超时秒数","number",1],["min_dpi","最低 DPI","number",1],["blur_threshold","模糊阈值","number",0]]],
  ["upload","上传限制",false,[["max_file_mb","单文件上限 MB","number",1],["max_zip_mb","ZIP 上限 MB","number",1],["allowed_ext","允许扩展名（逗号分隔）","list"]]],
  ["retention","保留期限",false,[["material_years","材料保留年数","number",1],["export_days","导出保留天数","number",1]]],
  ["notification","通知",false,[["in_app","站内消息","boolean"],["deadline_remind_days","提前提醒天数（逗号分隔）","numbers"],["email","邮件开关（需服务端支持）","boolean"],["sms","短信开关（需服务端支持）","boolean"]]],
  ["calendar","日历",false,[["holidays","节假日（YYYY-MM-DD，逗号或换行分隔）","dates"],["extra_workdays","调休工作日（YYYY-MM-DD，逗号或换行分隔）","dates"],["period_min_tail_days","末段最少天数","number",0]]],
  ["security","登录安全",true,[["max_failed_login","最大失败次数","number",1],["lock_minutes","锁定分钟数","number",1],["access_token_minutes","访问令牌分钟数","number",1],["refresh_token_days","刷新令牌天数","number",1]]],
  ["worker","后台任务",true,[["concurrency","任务并发数","number",1],["poll_interval_s","轮询间隔秒数","number",0.1],["heartbeat_timeout_s","心跳超时秒数","number",5]]],
]
export function settingsPatch(key, values) {
  const schema = SETTING_GROUPS.find((g) => g[0] === key)
  if (!schema) throw new Error("未知配置组")
  const out = {}
  for (const [field,label,type,min,max] of schema[3]) {
    const raw = values[field]
    if (raw == null || (raw === "" && !["list","dates","numbers"].includes(type))) continue
    if (type === "boolean") out[field] = !!raw
    else if (type === "number") {
      const n = Number(raw)
      if (!Number.isFinite(n) || n < min || (max != null && n > max)) throw new Error(`${label}超出允许范围`)
      if (!["temperature","classify_confidence_threshold","poll_interval_s","blur_threshold"].includes(field) && !Number.isInteger(n)) throw new Error(`${label}须为整数`)
      out[field] = n
    } else if (["list","dates","numbers"].includes(type)) {
      const list = Array.isArray(raw) ? raw : String(raw).split(/[,，\n]+/).map((s) => s.trim()).filter(Boolean)
      if (type === "dates" && list.some((s) => !validDate(s))) throw new Error(`${label}包含无效日期`)
      if (type === "numbers" && list.some((s) => !Number.isInteger(Number(s)) || Number(s) < 0)) throw new Error(`${label}须为非负整数`)
      out[field] = [...new Set(type === "numbers" ? list.map(Number) : list)]
    } else out[field] = String(raw).trim()
  }
  if (key === "ocr" && out.engine && !["auto","rapidocr","paddleocr","none"].includes(out.engine)) throw new Error("OCR 引擎须为 auto、rapidocr、paddleocr 或 none")
  return out
}
