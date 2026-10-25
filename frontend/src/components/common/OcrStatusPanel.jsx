import { useRef, useState } from "react"
import { testAi } from "../../api/settings"

export default function OcrStatusPanel({ settings = {}, disabled = false }) {
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const running = useRef(false)
  const check = async () => {
    if (running.current) return
    running.current = true
    setBusy(true)
    setResult(null)
    try {
      setResult(await testAi({ target: "ocr" }))
    } catch (error) {
      setResult({ ok: false, message: error.message || "OCR 自检请求失败，请重试" })
    } finally {
      running.current = false
      setBusy(false)
    }
  }
  return <section className="surface-card space-y-2 p-4">
    <h2 className="text-sm font-medium">OCR</h2>
    <p className="text-xs">已安装引擎 {(settings.available_engines || []).join("、") || "无"}；模型是否可用需运行识别自检。</p>
    <button type="button" className="btn btn-outline btn-sm" disabled={disabled || busy} onClick={check}>{busy ? "正在加载模型并识别…" : "测试 OCR"}</button>
    {busy && <p role="status" className="text-xs">首次运行可能需要下载模型，请等待识别完成。</p>}
    {result && <div role={result.ok ? "status" : "alert"} className={`text-xs ${result.ok ? "text-success" : "text-error"}`}>
      <p>{result.ok ? "识别自检通过" : "识别自检失败"} · {result.message} · {result.latency_ms ?? "—"} ms</p>
      {result.recognized_text && <p>测试图片识别结果：{result.recognized_text}</p>}
    </div>}
  </section>
}
