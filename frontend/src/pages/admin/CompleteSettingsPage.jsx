import { useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Loading, ErrorState } from "../../components/common/States"
import { getSettings, putSettings, seedDemo, testAi, testDelivery } from "../../api/settings"
import RetentionReview from "../../components/admin/RetentionReview"
import { useAuth } from "../../context/AuthContext"
import { SETTING_GROUPS, settingsPatch } from "../../utils/settingsWorkflow"
import { ConfirmDialog } from "../../components/common/Modal"

export default function CompleteSettingsPage() {
  const { activeRole } = useAuth()
  const isAdmin = activeRole?.role === "SYS_ADMIN"
  const [data, setData] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [busy, setBusy] = useState("")
  const [messages, setMessages] = useState({})
  const [apiKey, setApiKey] = useState("")
  const [clearKey, setClearKey] = useState(false)
  const [visionKey, setVisionKey] = useState("")
  const [clearVisionKey, setClearVisionKey] = useState(false)
  const [reset, setReset] = useState(false)
  const [deliverySecrets,setDeliverySecrets]=useState({})
  const [clearDeliverySecrets,setClearDeliverySecrets]=useState({})
  const load = () => { setLoadError(null); getSettings().then(setData).catch(setLoadError) }
  useEffect(load, [])
  const message = (key, text, error = false) => setMessages((m) => ({ ...m, [key]: { text, error } }))
  const set = (group, field, value) => setData((d) => ({ ...d, [group]: { ...d[group], [field]: value } }))
  const save = async (key) => {
    if (busy) return
    try {
      const patch = settingsPatch(key, data[key] || {})
      if (key === "ai" && (apiKey || clearKey)) patch.api_key = clearKey ? "" : apiKey
      if (key === "ocr_vision" && (visionKey || clearVisionKey)) patch.api_key = clearVisionKey ? "" : visionKey
      if (key === "delivery") for (const field of ["smtp_password","sms_api_key"]) {
        if (clearDeliverySecrets[field] || deliverySecrets[field]) patch[field]=clearDeliverySecrets[field] ? "" : deliverySecrets[field]
      }
      setBusy(key)
      const result = await putSettings({ [key]: patch })
      setData((d) => ({ ...d, [key]: result[key] }))
      if (key === "ai") { setApiKey(""); setClearKey(false) }
      if (key === "ocr_vision") { setVisionKey(""); setClearVisionKey(false) }
      if (key === "delivery") { setDeliverySecrets({}); setClearDeliverySecrets({}) }
      message(key, "已保存")
    } catch (e) { message(key, e.message || "保存失败", true) } finally { setBusy("") }
  }
  const test = async (key) => {
    if (busy) return
    setBusy(key)
    try {
      if(key === "delivery") {
        const result=await testDelivery()
        message(key,`${result.message}。邮件配置${result.email_ready ? "齐全" : "不完整"}；短信配置${result.sms_ready ? "齐全" : "不完整"}`)
        return
      }
      const result = await testAi({ target: key === "ai" ? "ocr_proofread_demo" : key })
      const demo = key === "ai" && result.sample
        ? `。样例：${result.sample}${result.corrections?.length ? `。建议：${result.corrections.map((item) => `“${item.original}”→“${item.suggestion}”（${item.reason}）`).join("；")}` : "。未返回确定的纠错建议"}`
        : ""
      message(key, `${result.ok ? "测试通过" : "测试失败"} · ${result.message || ""} · ${result.latency_ms ?? "—"} ms${demo}`, !result.ok)
    } catch (e) { message(key, e.message || "测试失败", true) } finally { setBusy("") }
  }
  const seed = async (resetData) => {
    if (busy) return
    setBusy("demo")
    try { const r = await seedDemo({ reset: resetData, run_checks: true }); message("demo", `演示档案 ${r.archives} · 用户 ${r.users}`); setReset(false) }
    catch (e) { message("demo", e.message || "初始化失败", true) } finally { setBusy("") }
  }
  if (loadError) return <ErrorState error={loadError} onRetry={load} />
  if (!data) return <Loading />
  return <div className="space-y-4">
    <PageHeader title="系统配置">按组保存。密钥不回显；组织部可编辑上传、保留期限、通知和日历。</PageHeader>
    <nav aria-label="配置分组" className="surface-card flex flex-wrap gap-2 p-3">{SETTING_GROUPS.map(([key, title]) => <a key={key} className="btn btn-ghost btn-sm" href={`#settings-${key}`}>{title}</a>)}</nav>
    <RetentionReview />
    {SETTING_GROUPS.map(([key,title,adminOnly,fields]) => <section key={key} id={`settings-${key}`} className="surface-card scroll-mt-6 p-4 sm:p-6" aria-label={title}>
      <div className="flex items-center justify-between gap-3 border-b border-base-200 pb-3"><h2 className="text-base font-semibold">{title}</h2><span className="text-xs text-base-content/55">{adminOnly && !isAdmin ? "只读" : "独立保存"}</span></div>
      <fieldset disabled={!!busy || (adminOnly && !isAdmin)} className="mt-3 grid gap-3 sm:grid-cols-2">
        {fields.map(([field,label,type]) => <label key={field} className={`form-control text-xs ${["dates","list","numbers"].includes(type) ? "sm:col-span-2" : ""}`}>{label}
          {type === "boolean" ? <input aria-label={label} type="checkbox" className="toggle toggle-sm mt-1" checked={!!data[key]?.[field]} onChange={(e) => set(key,field,e.target.checked)} />
            : <input aria-label={label} className="input input-bordered input-sm mt-1" type={type === "number" ? "number" : "text"} step={type === "number" ? "any" : undefined} value={Array.isArray(data[key]?.[field]) ? data[key][field].join(", ") : data[key]?.[field] ?? ""} onChange={(e) => set(key,field,e.target.value)} />}
        </label>)}
        {key === "ai" && <><label className="form-control text-xs">API 密钥（留空保留）<input aria-label="API 密钥" type="password" autoComplete="new-password" className="input input-bordered input-sm mt-1" disabled={clearKey} placeholder={data.ai?.api_key_set ? "已设置" : "未设置"} value={apiKey} onChange={(e) => setApiKey(e.target.value)} /></label><label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={clearKey} onChange={(e) => setClearKey(e.target.checked)} />清除已保存密钥</label></>}
        {key === "ocr_vision" && <><label className="form-control text-xs">视觉模型 API 密钥（留空保留）<input aria-label="视觉模型 API 密钥" type="password" autoComplete="new-password" className="input input-bordered input-sm mt-1" disabled={clearVisionKey} placeholder={data.ocr_vision?.api_key_set ? "已设置" : "未设置"} value={visionKey} onChange={(e) => setVisionKey(e.target.value)} /></label><label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={clearVisionKey} onChange={(e) => setClearVisionKey(e.target.checked)} />清除视觉模型密钥</label></>}
        {key === "delivery" && [["smtp_password","SMTP 密码"],["sms_api_key","短信 API 密钥"]].map(([field,label])=><div key={field} className="space-y-1 text-xs"><label>{label}（留空保留）<input type="password" aria-label={label} autoComplete="new-password" className="input input-bordered input-sm w-full" disabled={!!clearDeliverySecrets[field]} placeholder={data.delivery?.[field+"_set"] ? "已设置" : "未设置"} value={deliverySecrets[field] || ""} onChange={e=>setDeliverySecrets(v=>({...v,[field]:e.target.value}))} /></label><label className="flex items-center gap-2"><input type="checkbox" checked={!!clearDeliverySecrets[field]} onChange={e=>setClearDeliverySecrets(v=>({...v,[field]:e.target.checked}))} />清除{label}</label></div>)}
      </fieldset>
      {["delivery","notification"].includes(key) && <p className="mt-2 text-xs text-base-content/60">邮件短信目前仅配置和检查，不实际投递；站内消息照常使用。密钥加密保存，不回显。</p>}
      {key === "ocr_vision" && <p className="mt-2 rounded bg-warning/10 p-2 text-xs">真实材料复核使用本组的视觉模型配置，与上方“大模型”配置和密钥分开。使用支持图片输入及 Chat Completions 格式的模型服务，分别填写接口基础地址、模型名称与该服务密钥。更换服务地址后须重新保存对应密钥。各服务和模型需分别测试。下方测试只发送系统内置虚构图片。保存并开启“启用视觉 OCR 复核”和“允许将材料原图区域发送至所配置的模型服务”后，新上传或重新解析的扫描件会自动发送符合条件的页面；若要检查整页（包括高置信度 OCR 可能漏掉的错误），同时开启“复核所有扫描页”。图片和 OCR 原文会发送给配置的服务，不经过脱敏；测试时只上传你获准使用的一份材料，完成后关闭前两个开关。模型只提供转录建议，不会覆盖 RapidOCR 原文；请在材料详情的“解析文本”中对照原图核实，再手动校正并保存。</p>}
      {key === "ai" && <p className="mt-2 rounded bg-warning/10 p-2 text-xs text-base-content">文本模型接入：填写兼容 Chat Completions 的接口基础地址、模型名和该服务 API 密钥后保存。下方测试只发送系统内置的虚构 OCR 文本“抗5战胜利80周年”，不会读取或上传材料；测试结果仅展示建议，不会修改任何材料。开启“启用大模型”后，审核流程会按配置向该服务发送材料文本；脱敏用于减少身份信息，仍会发送材料内容。</p>}
      {key === "ocr" && <p className="mt-2 text-xs text-base-content/60">已发现引擎：{(data.ocr?.available_engines || []).join("、") || "无"}。测试识别内置图片；未安装引擎时会报告不可用。</p>}
      {key === "worker" && <p className="mt-2 text-xs text-base-content/60">任务并发数的调整在服务重新启动后生效。</p>}
      <div className="mt-3 flex gap-2"><button type="button" className="btn btn-primary btn-sm" disabled={!!busy || (adminOnly && !isAdmin)} onClick={() => save(key)}>保存{title}</button>{["ai","ocr","ocr_vision","delivery"].includes(key) && <button type="button" className="btn btn-outline btn-sm" disabled={!!busy || !isAdmin} onClick={() => test(key)}>{key === "delivery" ? "检查投递配置（不发送）" : key === "ai" ? "测试虚构文本校对" : `测试${title}`}</button>}</div>
      {messages[key] && <p role="status" className={`mt-2 text-xs ${messages[key].error ? "text-error" : "text-success"}`}>{messages[key].text}</p>}
    </section>)}
    <section className="surface-card space-y-3 p-4"><h2 className="text-sm font-medium">演示数据</h2><p className="text-xs">生成独立标记的虚构组织、账号和材料。</p><div className="flex gap-2"><button type="button" className="btn btn-outline btn-sm" disabled={!!busy} onClick={() => seed(false)}>初始化</button><button type="button" className="btn btn-ghost btn-sm" disabled={!!busy} onClick={() => setReset(true)}>清理并重建</button></div>{messages.demo && <p role="status" className={messages.demo.error ? "text-error" : "text-success"}>{messages.demo.text}</p>}</section>
    <ConfirmDialog open={reset} danger title="重建演示数据" confirmText="确认重建" busy={!!busy} message="仅删除并重建标记为演示的数据，真实账号和真实材料不会被清理。操作不可撤销，确认继续？" onClose={() => setReset(false)} onConfirm={() => seed(true)} />
  </div>
}
