import { fmtDateTime, fmtSize } from "../../utils/format"

export default function VersionList({ versions = [], currentId, onSelect }) {
  if (!versions.length) return <p className="text-sm text-base-content/50">没有历史版本。</p>
  return (
    <ul className="space-y-2">
      {versions.map((v) => (
        <li key={v.id} className={`surface-card flex items-center justify-between gap-2 p-3 text-sm ${currentId === v.id ? "border-primary" : ""}`}>
          <div>
            <div className="font-medium">第 {v.version_no} 版 {v.is_current && <span className="badge badge-primary badge-xs ml-1">当前</span>}</div>
            <div className="text-xs text-base-content/55">
              {v.original_filename} · {fmtSize(v.file_size)} · {v.parse_status} · {fmtDateTime(v.uploaded_at)}
            </div>
            {v.change_note && <div className="text-xs">{v.change_note}</div>}
          </div>
          {onSelect && <button type="button" className="btn btn-ghost btn-xs" onClick={() => onSelect(v)}>查看</button>}
        </li>
      ))}
    </ul>
  )
}
