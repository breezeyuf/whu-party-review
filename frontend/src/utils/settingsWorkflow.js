import { validDate } from "./adminWorkflow.js"
export const SETTING_GROUPS = [
  ["auth","登录方式",true,[["mode","认证模式（demo / sso）","text"],["login_url","CAS 登录 HTTPS 地址","text"],["validate_url","CAS 验票 HTTPS 地址","text"]]],
  ["delivery","邮件与短信服务配置",true,[["smtp_host","SMTP 主机","text"],["smtp_port","SMTP 端口","number",1,65535],["smtp_username","SMTP 用户名","text"],["smtp_sender","发件地址","text"],["smtp_security","SMTP 加密方式（ssl / starttls）","text"],["sms_url","短信服务 HTTPS 接口","text"],["sms_sender","短信签名","text"],["sms_template_id","短信模板编号","text"]]],
  ["ai", "大模型", true, [["llm_enabled","启用大模型","boolean"],["base_url","接口地址","text"],["model","模型名","text"],["timeout_s","超时秒数","number",1,600],["max_concurrency","最大并发","number",1,32],["temperature","温度","number",0,2],["desensitize","调用前脱敏","boolean"],["classify_confidence_threshold","分类置信度阈值","number",0,1]]],
  ["ocr","OCR",true,[["engine","引擎（auto、rapidocr 或 none）","text"],["timeout_s","超时秒数","number",1,600],["min_dpi","最低 DPI","number",72,300],["blur_threshold","模糊阈值","number",0,100000]]],
  ["ocr_vision","视觉 OCR 复核",true,[["enabled","启用视觉 OCR 复核","boolean"],["allow_image_upload","允许将材料原图区域发送至所配置的模型服务","boolean"],["base_url","视觉模型接口地址","text"],["model","视觉模型名称","text"],["timeout_s","视觉请求超时秒数","number",1,120],["confidence_threshold","低置信度复核阈值","number",0,1],["max_regions","每份材料最多复核区域数","number",1,20],["review_all","复核所有扫描页（包括高置信度和手写内容）","boolean"]]],
  ["upload","上传限制",false,[["max_file_mb","单文件上限 MB","number",1],["max_zip_mb","ZIP 上限 MB","number",1],["allowed_ext","允许扩展名（逗号分隔）","list"]]],
  ["retention","保留期限",false,[["material_years","材料保留年数","number",1,100],["export_days","导出保留天数","number",1]]],
  ["notification","通知",false,[["in_app","站内消息","boolean"],["deadline_remind_days","提前提醒天数（逗号分隔）","numbers"],["email","邮件开关（需服务端支持）","boolean"],["sms","短信开关（需服务端支持）","boolean"]]],
  ["calendar","日历",false,[["holidays","节假日（YYYY-MM-DD，逗号或换行分隔）","dates"],["extra_workdays","调休工作日（YYYY-MM-DD，逗号或换行分隔）","dates"],["period_min_tail_days","末段最少天数","number",0]]],
  ["security","登录安全",true,[["max_failed_login","最大失败次数","number",1],["lock_minutes","锁定分钟数","number",1],["access_token_minutes","登录有效分钟数","number",1,1440]]],
  ["worker","后台任务",true,[["concurrency","任务并发数","number",1],["poll_interval_s","轮询间隔秒数","number",0.1],["heartbeat_timeout_s","心跳超时秒数","number",5]]],
]
export function settingsPatch(key, values) {
  const schema = SETTING_GROUPS.find((g) => g[0] === key)
  if (!schema) throw new Error("未知配置组")
  const out = {}
  for (const [field,label,type,min,max] of schema[3]) {
    const raw = values[field]
    if (raw == null || (raw === "" && !["text","list","dates","numbers"].includes(type))) continue
    if (type === "boolean") out[field] = !!raw
    else if (type === "number") {
      const n = Number(raw)
      if (!Number.isFinite(n) || n < min || (max != null && n > max)) throw new Error(`${label}超出允许范围`)
      if (!["temperature","classify_confidence_threshold","confidence_threshold","poll_interval_s","blur_threshold"].includes(field) && !Number.isInteger(n)) throw new Error(`${label}须为整数`)
      out[field] = n
    } else if (["list","dates","numbers"].includes(type)) {
      const list = Array.isArray(raw) ? raw : String(raw).split(/[,，\n]+/).map((s) => s.trim()).filter(Boolean)
      if (type === "dates" && list.some((s) => !validDate(s))) throw new Error(`${label}包含无效日期`)
      if (type === "numbers" && list.some((s) => !Number.isInteger(Number(s)) || Number(s) < 0)) throw new Error(`${label}须为非负整数`)
      out[field] = [...new Set(type === "numbers" ? list.map(Number) : list)]
    } else out[field] = String(raw).trim()
  }
  if (key === "ocr" && out.engine && !["auto","rapidocr","none"].includes(out.engine)) throw new Error("OCR 引擎须为 auto、rapidocr 或 none")
  if (key === "auth" && !["demo","sso"].includes(out.mode)) throw new Error("认证模式须为 demo 或 sso")
  return out
}
