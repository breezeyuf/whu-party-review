import { saveBlob } from "../../api/client"
import { exportNotice } from "../../api/notices"
import { useState } from "react"
import { SeverityBadge } from "../common/Badges"

export default function NoticePreview({ notice }) {
  const [busy, setBusy] = useState("")
  if (!notice) return <p className="text-sm text-base-content/50">选择一条通知查看。</p>
  const content = notice.content || {}
  const items = content.items || []
  const completion = content.completion_items || []

  const download = async (format) => {
    setBusy(format)
    try {
      const file = await exportNotice(notice.id, format)
      saveBlob(file)
    } finally {
      setBusy("")
    }
  }

  return (
    <article className="surface-card p-4">
      <header className="border-b border-base-300 pb-3">
        <h2 className="text-base font-semibold">{notice.title}</h2>
        <p className="mt-1 text-xs text-base-content/55">
          {content.student?.name} · {content.student?.student_no} · {content.student?.branch} · {content.stage}
        </p>
        <p className="text-xs text-base-content/55">截止日期 {notice.deadline || "—"} · {notice.status}</p>
      </header>
      {content.intro && <p className="mt-3 text-sm">{content.intro}</p>}
      <ol className="mt-3 space-y-3">
        {items.map((it) => (
          <li key={it.no || it.issue_id} className="text-sm">
            <div className="flex flex-wrap items-center gap-2">
              <span className="mono text-xs">{it.no}.</span>
              <SeverityBadge code={it.severity === "阻断" ? "BLOCK" : it.severity === "警告" ? "WARN" : it.severity} />
              <span>{it.material}</span>
              <span className="text-xs text-base-content/50">{it.location}</span>
            </div>
            <p className="mt-1">{it.problem}</p>
            {it.basis && <p className="text-xs text-base-content/55">依据：{it.basis}</p>}
            {it.suggestion && <p className="text-xs">建议：{it.suggestion}</p>}
          </li>
        ))}
      </ol>
      {completion.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium">材料补全</h3>
          <ul className="mt-1 list-disc pl-5 text-sm">
            {completion.map((c, i) => <li key={i}>{c.material || c.material_name || c.name || "材料"} · 缺 {c.missing ?? c.missing_count ?? "—"} 份 {c.requirement ? `· ${c.requirement}` : ""}</li>)}
          </ul>
        </div>
      )}
      {content.note && <p className="mt-3 whitespace-pre-wrap text-sm">审核意见：{content.note}</p>}
      <div className="mt-4 flex gap-2">
        <button type="button" className="btn btn-outline btn-sm" disabled={!!busy} onClick={() => download("pdf")}>{busy === "pdf" ? "导出中" : "导出 PDF"}</button>
        <button type="button" className="btn btn-ghost btn-sm" disabled={!!busy} onClick={() => download("docx")}>{busy === "docx" ? "导出中" : "导出 Word"}</button>
      </div>
    </article>
  )
}
