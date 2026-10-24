import { useCallback, useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Loading, ErrorState } from "../../components/common/States"
import { ConfirmDialog } from "../../components/common/Modal"
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
  const [retention, setRetention] = useState({})
  const [calendar, setCalendar] = useState({})
  const [test, setTest] = useState(null)
  const [testing, setTesting] = useState("")
  const [aiSaving, setAiSaving] = useState(false)
  const [uploadSaving, setUploadSaving] = useState(false)
  const [retentionSaving, setRetentionSaving] = useState(false)
  const [calendarSaving, setCalendarSaving] = useState(false)
  const [demoBusy, setDemoBusy] = useState(false)
  const [confirmDemoReset, setConfirmDemoReset] = useState(false)
  const [seedMsg, setSeedMsg] = useState("")

  const load = useCallback(() => {
    setError(null)
    return getSettings().then((d) => {
      setData(d)
      setAi(d.ai || {})
      setOcr(d.ocr || {})
      setUpload(d.upload || {})
      setRetention(d.retention || {})
      const calendarData = d.calendar || {}
      setCalendar({ ...calendarData, holidays_text: (calendarData.holidays || []).join("\n"), extra_workdays_text: (calendarData.extra_workdays || []).join("\n") })
    }).catch(setError)
  }, [])
  useEffect(() => { load() }, [load])

  const saveAi = async () => {
    if (aiSaving) return
    const body = { ai: { base_url: ai.base_url, model: ai.model, timeout_s: Number(ai.timeout_s), max_concurrency: Number(ai.max_concurrency), llm_enabled: !!ai.llm_enabled, desensitize: ai.desensitize !== false } }
    if (ai.api_key) body.ai.api_key = ai.api_key
    setAiSaving(true)
    try {
      await putSettings(body)
      toast.success("AI 配置已保存")
      await load()
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setAiSaving(false)
    }
  }

  const runTest = async (target) => {
    if (testing) return
    setTesting(target)
    try {
      const result = await testAi({ target })
      if (target === "llm") {
        setTest(result)
        if (!result.ok) toast.error(result.message || "模型连通性测试失败")
      } else {
        toast.info(result.ok ? `OCR 可用 · ${result.message}` : (result.message || "OCR 不可用"))
      }
    } catch (e) {
      if (target === "llm") setTest({ ok: false, message: e.message || "请求失败" })
      toast.error(e.message || "测试请求失败")
    } finally {
      setTesting("")
    }
  }

  const saveUpload = async () => {
    const fileLimit = Number(upload.max_file_mb)
    const zipLimit = Number(upload.max_zip_mb)
    if (!Number.isInteger(fileLimit) || fileLimit < 1 || fileLimit > 2048) {
      toast.error("单份材料上限须为 1–2048 MB 的整数")
      return
    }
    if (!Number.isInteger(zipLimit) || zipLimit < 1 || zipLimit > 2048) {
      toast.error("ZIP 压缩包上限须为 1–2048 MB 的整数")
      return
    }
    setUploadSaving(true)
    try {
      await putSettings({ upload: { ...upload, max_file_mb: fileLimit, max_zip_mb: zipLimit } })
      toast.success("上传限制已保存")
      await load()
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setUploadSaving(false)
    }
  }

  const saveRetention = async () => {
    const exportDays = Number(retention.export_days)
    if (!Number.isInteger(exportDays) || exportDays < 1 || exportDays > 365) {
      toast.error("导出文件有效期须为 1–365 天的整数")
      return
    }
    setRetentionSaving(true)
    try {
      await putSettings({ retention: { ...retention, export_days: exportDays } })
      toast.success("导出保留期限已保存")
      await load()
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setRetentionSaving(false)
    }
  }

  const saveCalendar = async () => {
    const periodDays = Number(calendar.period_min_tail_days)
    if (!Number.isInteger(periodDays) || periodDays < 0 || periodDays > 365) {
      toast.error("周期末段最少天数须为 0–365 天的整数")
      return
    }
    const parseDates = (value) => String(value || "").split(/\r?\n|[,，;；]/).map((date) => date.trim()).filter(Boolean)
    const holidays = parseDates(calendar.holidays_text)
    const extraWorkdays = parseDates(calendar.extra_workdays_text)
    const validDate = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(`${value}T00:00:00Z`)) && new Date(`${value}T00:00:00Z`).toISOString().slice(0, 10) === value
    if ([...holidays, ...extraWorkdays].some((date) => !validDate(date))) {
      toast.error("日期请使用有效的 YYYY-MM-DD 格式，每行填写一个")
      return
    }
    if (new Set([...holidays, ...extraWorkdays]).size !== holidays.length + extraWorkdays.length) {
      toast.error("节假日和调休日不能重复填写")
      return
    }
    setCalendarSaving(true)
    try {
      const { holidays_text: _holidaysText, extra_workdays_text: _extraWorkdaysText, ...savedCalendar } = calendar
      await putSettings({ calendar: { ...savedCalendar, period_min_tail_days: periodDays, holidays: [...new Set(holidays)].sort(), extra_workdays: [...new Set(extraWorkdays)].sort() } })
      toast.success("工作日历已保存")
      await load()
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setCalendarSaving(false)
    }
  }

  const seed = async (reset) => {
    if (demoBusy) return
    setDemoBusy(true)
    setSeedMsg("")
    try {
      const result = await seedDemo({ reset, run_checks: true })
      const message = result.message || (reset ? "演示数据已清理并重建" : "演示数据初始化完成")
      const counts = result.archives != null
        ? `组织 ${result.orgs} · 用户 ${result.users} · 档案 ${result.archives} · 材料 ${result.materials}`
        : `${result.accounts?.length || 0} 个演示账号已存在`
      setSeedMsg(`${message} · ${counts}`)
      toast.success(message)
      setConfirmDemoReset(false)
    } catch (e) {
      toast.error(e.message || "演示数据操作失败")
    } finally {
      setDemoBusy(false)
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
          <button type="button" className="btn btn-primary btn-sm" disabled={!isAdmin || aiSaving} onClick={saveAi}>{aiSaving ? "保存中…" : "保存"}</button>
          <button type="button" className="btn btn-outline btn-sm" disabled={!isAdmin || !!testing} onClick={() => runTest("llm")}>{testing === "llm" ? "测试中…" : "连通性测试"}</button>
        </div>
        {test && <p className={`text-xs ${test.ok ? "text-success" : "text-error"}`}>{test.ok ? "连通" : "失败"} · {test.latency_ms ?? "—"} ms · {test.message}</p>}
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">OCR</h2>
        <p className="text-xs">当前引擎 {ocr.engine || "—"} · 可用 {(ocr.available_engines || []).join("、") || "无"}</p>
        <button type="button" className="btn btn-outline btn-sm" disabled={!isAdmin || !!testing} onClick={() => runTest("ocr")}>{testing === "ocr" ? "测试中…" : "测试 OCR"}</button>
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">上传限制</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="form-control"><span className="label-text text-xs">单份材料上限（MB）</span><input className="input input-bordered input-sm" type="number" min="1" max="2048" step="1" value={upload.max_file_mb ?? ""} onChange={(e) => setUpload({ ...upload, max_file_mb: e.target.value })} /></label>
          <label className="form-control"><span className="label-text text-xs">ZIP 压缩包上限（MB）</span><input className="input input-bordered input-sm" type="number" min="1" max="2048" step="1" value={upload.max_zip_mb ?? ""} onChange={(e) => setUpload({ ...upload, max_zip_mb: e.target.value })} /></label>
        </div>
        <p className="text-xs text-base-content/55">影响学生单份材料上传和管理员批量 ZIP 导入。修改后由后端实际执行限制。</p>
        <button type="button" className="btn btn-primary btn-sm" disabled={uploadSaving} onClick={saveUpload}>{uploadSaving ? "保存中…" : "保存上传限制"}</button>
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">导出文件保留期限</h2>
        <p className="text-xs text-base-content/55">只影响之后新生成的导出文件；已有文件的到期时间不变。</p>
        <label className="form-control max-w-xs"><span className="label-text text-xs">可下载天数</span><input className="input input-bordered input-sm" type="number" min="1" max="365" step="1" value={retention.export_days ?? ""} onChange={(e) => setRetention({ ...retention, export_days: e.target.value })} /></label>
        <button type="button" className="btn btn-primary btn-sm" disabled={retentionSaving} onClick={saveRetention}>{retentionSaving ? "保存中…" : "保存保留期限"}</button>
      </section>
      <section className="surface-card space-y-3 p-4">
        <h2 className="text-sm font-medium">工作日历</h2>
        <p className="text-xs text-base-content/55">用于工作日间隔和周期材料核对。修改后新启动的 AI 核对采用新日历；已有报告需要重新核对。</p>
        <label className="form-control"><span className="label-text text-xs">节假日（每行一个 YYYY-MM-DD）</span><textarea className="textarea textarea-bordered text-sm" rows={3} placeholder="2026-10-01" value={calendar.holidays_text || ""} onChange={(e) => setCalendar({ ...calendar, holidays_text: e.target.value })} /></label>
        <label className="form-control"><span className="label-text text-xs">调休日（每行一个 YYYY-MM-DD）</span><textarea className="textarea textarea-bordered text-sm" rows={3} placeholder="2026-10-10" value={calendar.extra_workdays_text || ""} onChange={(e) => setCalendar({ ...calendar, extra_workdays_text: e.target.value })} /></label>
        <label className="form-control max-w-xs"><span className="label-text text-xs">周期末段最少天数</span><input className="input input-bordered input-sm" type="number" min="0" max="365" step="1" value={calendar.period_min_tail_days ?? ""} onChange={(e) => setCalendar({ ...calendar, period_min_tail_days: e.target.value })} /></label>
        <button type="button" className="btn btn-primary btn-sm" disabled={calendarSaving} onClick={saveCalendar}>{calendarSaving ? "保存中…" : "保存工作日历"}</button>
      </section>
      <section className="surface-card space-y-2 p-4">
        <h2 className="text-sm font-medium">演示数据</h2>
        <p className="text-xs text-base-content/60">生成虚构组织、账号和带预设问题的材料。真实数据请用导入，两者在库中分开标记。</p>
        <div className="flex gap-2">
          <button type="button" className="btn btn-outline btn-sm" disabled={demoBusy} onClick={() => seed(false)}>{demoBusy ? "处理中…" : "初始化"}</button>
          <button type="button" className="btn btn-ghost btn-sm" disabled={demoBusy} onClick={() => setConfirmDemoReset(true)}>清理并重建</button>
        </div>
        {seedMsg && <p className="text-xs">{seedMsg}</p>}
      </section>
      <ConfirmDialog open={confirmDemoReset} danger busy={demoBusy} title="清理并重建演示数据" message="这会删除并重新生成演示账号、演示档案及其演示材料。真实账号和真实材料不会被清理。确认继续吗？" confirmText="确认重建" onClose={() => { if (!demoBusy) setConfirmDemoReset(false) }} onConfirm={() => seed(true)} />
    </div>
  )
}
