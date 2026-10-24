import { useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Loading, ErrorState } from "../../components/common/States"
import { getSettings, putSettings, seedDemo, testAi } from "../../api/settings"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"

export default function SettingsPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const isAdmin = activeRole?.role === "SYS_ADMIN"
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [ai, setAi] = useState({})
  const [ocr, setOcr] = useState({})
  const [upload, setUpload] = useState({})
  const [test, setTest] = useState(null)
  const [seedMsg, setSeedMsg] = useState("")

  const load = () => {
    setError(null)
    getSettings().then((d) => {
      setData(d)
      setAi(d.ai || {})
      setOcr(d.ocr || {})
      setUpload(d.upload || {})
    }).catch(setError)
  }
  useEffect(load, [])

  const saveAi = async () => {
    const body = { ai: { base_url: ai.base_url, model: ai.model, timeout_s: Number(ai.timeout_s), max_concurrency: Number(ai.max_concurrency), llm_enabled: !!ai.llm_enabled, desensitize: ai.desensitize !== false } }
    if (ai.api_key) body.ai.api_key = ai.api_key
    try {
      await putSettings(body)
      toast.success("AI 配置已保存")
      load()
    } catch (e) {
      toast.error(e.message || "保存失败")
    }
  }

  if (!data && !error) return <Loading />
  if (error) return <ErrorState error={error} onRetry={load} />

  return (
    <div className="space-y-4">
      <PageHeader title="系统配置" />
      <section className="surface-card space-y-3 p-4">
        <h2 className="text-sm font-medium">大模型</h2>
        <p className="text-xs text-base-content/55">密钥只显示是否已设置，不会回显。更换接口地址时请重新填写密钥。未配置时审核降级为仅规则模式。</p>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="toggle toggle-sm" checked={!!ai.llm_enabled} disabled={!isAdmin} onChange={(e) => setAi({ ...ai, llm_enabled: e.target.checked })} />启用</label>
        <input className="input input-bordered input-sm w-full" placeholder="接口地址" disabled={!isAdmin} value={ai.base_url || ""} onChange={(e) => setAi({ ...ai, base_url: e.target.value })} />
        <input className="input input-bordered input-sm w-full" placeholder="模型名" disabled={!isAdmin} value={ai.model || ""} onChange={(e) => setAi({ ...ai, model: e.target.value })} />
        <input className="input input-bordered input-sm w-full" type="password" placeholder={ai.api_key_set ? "已设置密钥，留空表示不修改" : "API 密钥"} disabled={!isAdmin} value={ai.api_key || ""} onChange={(e) => setAi({ ...ai, api_key: e.target.value })} />
        <div className="flex gap-2">
          <button type="button" className="btn btn-primary btn-sm" disabled={!isAdmin} onClick={saveAi}>保存</button>
          <button type="button" className="btn btn-outline btn-sm" disabled={!isAdmin} onClick={async () => setTest(await testAi({ target: "llm" }))}>连通性测试</button>
        </div>
        {test && <p className={`text-xs ${test.ok ? "text-success" : "text-error"}`}>{test.ok ? "连通" : "失败"} · {test.latency_ms ?? "—"} ms · {test.message}</p>}
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">OCR</h2>
        <p className="text-xs">当前引擎 {ocr.engine || "—"} · 可用 {(ocr.available_engines || []).join("、") || "无"}</p>
        <button type="button" className="btn btn-outline btn-sm" disabled={!isAdmin} onClick={async () => { const r = await testAi({ target: "ocr" }); toast.info(r.ok ? "OCR 可用" : (r.message || "OCR 不可用")) }}>测试 OCR</button>
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">上传限制</h2>
        <input className="input input-bordered input-sm w-40" type="number" value={upload.max_mb || ""} onChange={(e) => setUpload({ ...upload, max_mb: Number(e.target.value) })} />
        <button type="button" className="btn btn-primary btn-sm ml-2" onClick={async () => {
          try {
            await putSettings({ upload })
            toast.success("已保存")
          } catch (e) {
            toast.error(e.message || "保存失败")
          }
        }}>保存</button>
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">演示数据</h2>
        <p className="text-xs text-base-content/60">生成虚构组织、账号和带预设问题的材料。真实数据请用导入，两者在库中分开标记。</p>
        <div className="flex gap-2">
          <button type="button" className="btn btn-outline btn-sm" onClick={async () => { const r = await seedDemo({ reset: false, run_checks: true }); setSeedMsg(`组织 ${r.orgs} · 用户 ${r.users} · 档案 ${r.archives}`) }}>初始化</button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={async () => { const r = await seedDemo({ reset: true, run_checks: true }); setSeedMsg(`已重建 · 档案 ${r.archives}`) }}>清理并重建</button>
        </div>
        {seedMsg && <p className="text-xs">{seedMsg}</p>}
      </section>
    </div>
  )
}
