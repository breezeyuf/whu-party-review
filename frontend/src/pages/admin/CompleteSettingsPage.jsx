import { useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Loading, ErrorState } from "../../components/common/States"
import { getSettings, putSettings, seedDemo, testAi } from "../../api/settings"
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
      setBusy(key)
      const result = await putSettings({ [key]: patch })
      setData((d) => ({ ...d, [key]: result[key] }))
      if (key === "ai") { setApiKey(""); setClearKey(false) }
      if (key === "ocr_vision") { setVisionKey(""); setClearVisionKey(false) }
      message(key, "已保存")
    } catch (e) { message(key, e.message || "保存失败", true) } finally { setBusy("") }
  }
  const test = async (key) => {
    if (busy) return
    setBusy(key)
    try {
      const result = await testAi({ target: key === "ai" ? "llm" : key })
      message(key, `${result.ok ? "测试通过" : "测试失败"} · ${result.message || ""} · ${result.latency_ms ?? "—"} ms`, !result.ok)
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
    {SETTING_GROUPS.map(([key,title,adminOnly,fields]) => <details key={key} className="surface-card p-4" open={key === "ai" ? true : undefined}>
      <summary className="cursor-pointer text-sm font-medium">{title}{adminOnly && !isAdmin ? "（只读）" : ""}</summary>
      <fieldset disabled={!!busy || (adminOnly && !isAdmin)} className="mt-3 grid gap-3 sm:grid-cols-2">
        {fields.map(([field,label,type]) => <label key={field} className={`form-control text-xs ${["dates","list","numbers"].includes(type) ? "sm:col-span-2" : ""}`}>{label}
          {type === "boolean" ? <input aria-label={label} type="checkbox" className="toggle toggle-sm mt-1" checked={!!data[key]?.[field]} onChange={(e) => set(key,field,e.target.checked)} />
            : <input aria-label={label} className="input input-bordered input-sm mt-1" type={type === "number" ? "number" : "text"} step={type === "number" ? "any" : undefined} value={Array.isArray(data[key]?.[field]) ? data[key][field].join(", ") : data[key]?.[field] ?? ""} onChange={(e) => set(key,field,e.target.value)} />}
        </label>)}
        {key === "ai" && <><label className="form-control text-xs">API 密钥（留空保留）<input aria-label="API 密钥" type="password" autoComplete="new-password" className="input input-bordered input-sm mt-1" disabled={clearKey} placeholder={data.ai?.api_key_set ? "已设置" : "未设置"} value={apiKey} onChange={(e) => setApiKey(e.target.value)} /></label><label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={clearKey} onChange={(e) => setClearKey(e.target.checked)} />清除已保存密钥</label></>}
        {key === "ocr_vision" && <><label className="form-control text-xs">视觉模型 API 密钥（留空保留）<input aria-label="视觉模型 API 密钥" type="password" autoComplete="new-password" className="input input-bordered input-sm mt-1" disabled={clearVisionKey} placeholder={data.ocr_vision?.api_key_set ? "已设置" : "未设置"} value={visionKey} onChange={(e) => setVisionKey(e.target.value)} /></label><label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={clearVisionKey} onChange={(e) => setClearVisionKey(e.target.checked)} />清除视觉模型密钥</label></>}
      </fieldset>
      {key === "ocr_vision" && <p className="mt-2 text-xs text-base-content/60">使用支持图片输入的兼容接口（地址通常以 /v1 结尾）。先保存再测试，测试仅发送内置虚构图片。启用并允许发送后，新上传或重新解析的扫描材料会进行复核；图片不经过文字脱敏。模型建议须在材料的解析文本面板核对后保存，失败保留本地 OCR 结果。手写材料可开启所有扫描页复核。</p>}
      {key === "ocr" && <p className="mt-2 text-xs text-base-content/60">已发现引擎：{(data.ocr?.available_engines || []).join("、") || "无"}。测试识别内置图片；未安装引擎时会报告不可用。</p>}
      {key === "worker" && <p className="mt-2 text-xs text-base-content/60">任务并发数的调整在服务重新启动后生效。</p>}
      <div className="mt-3 flex gap-2"><button type="button" className="btn btn-primary btn-sm" disabled={!!busy || (adminOnly && !isAdmin)} onClick={() => save(key)}>保存{title}</button>{["ai","ocr","ocr_vision"].includes(key) && <button type="button" className="btn btn-outline btn-sm" disabled={!!busy || !isAdmin} onClick={() => test(key)}>测试{title}</button>}</div>
      {messages[key] && <p role="status" className={`mt-2 text-xs ${messages[key].error ? "text-error" : "text-success"}`}>{messages[key].text}</p>}
    </details>)}
    <section className="surface-card space-y-3 p-4"><h2 className="text-sm font-medium">演示数据</h2><p className="text-xs">生成独立标记的虚构组织、账号和材料。</p><div className="flex gap-2"><button type="button" className="btn btn-outline btn-sm" disabled={!!busy} onClick={() => seed(false)}>初始化</button><button type="button" className="btn btn-ghost btn-sm" disabled={!!busy} onClick={() => setReset(true)}>清理并重建</button></div>{messages.demo && <p role="status" className={messages.demo.error ? "text-error" : "text-success"}>{messages.demo.text}</p>}</section>
    <ConfirmDialog open={reset} danger title="重建演示数据" message="仅删除并重建标记为演示的数据，操作不可撤销。确认继续？" onClose={() => setReset(false)} onConfirm={() => seed(true)} />
  </div>
}
