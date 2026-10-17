import { Link } from "react-router-dom"
import FileUploader from "../common/FileUploader"
import { fmtDateTime } from "../../utils/format"

export default function ChecklistPanel({ groups = [], canUpload, onUpload, onPreview }) {
  if (!groups.length) {
    return <p className="text-sm text-base-content/50">当前阶段还没有材料清单。请先完成档案创建，或联系组织部配置规则。</p>
  }
  return (
    <div className="space-y-4">
      {groups.map((g) => (
        <section key={g.stage_code} className="space-y-3">
          {(g.checklist || []).map((item) => {
            const missing = item.missing_count > 0
            return (
              <div key={item.checklist_item_id || item.material_type?.id} className="surface-card p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <div className="text-sm font-medium">
                      {item.material_type?.name || item.material_type}
                      {item.required && <span className="badge badge-outline badge-xs ml-2">必需</span>}
                      {missing && <span className="badge badge-error badge-xs ml-2">缺 {item.missing_count}</span>}
                    </div>
                    <div className="mono mt-1 text-xs text-base-content/55">
                      应交 {item.expected_count ?? "—"} · 已交 {item.actual_count ?? 0}
                    </div>
                    {item.requirement_text && <p className="mt-1 text-xs text-base-content/60">{item.requirement_text}</p>}
                  </div>
                </div>
                <ul className="mt-2 divide-y divide-base-200">
                  {(item.materials || []).map((m) => (
                    <li key={m.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
                      <div>
                        <button type="button" className="link" onClick={() => onPreview?.(m)}>{m.title || `材料 #${m.id}`}</button>
                        {m.type_status === "NEEDS_CONFIRM" && <span className="badge badge-warning badge-xs ml-2">待确认类型</span>}
                        <div className="text-xs text-base-content/50">
                          v{m.current_version?.version_no || 1} · {m.current_version?.parse_status || "待解析"} · {fmtDateTime(m.current_version?.uploaded_at)}
                          {m.open_issue_count ? ` · 问题 ${m.open_issue_count}` : ""}
                        </div>
                      </div>
                      <Link className="btn btn-ghost btn-xs" to={`/materials/${m.id}`}>详情</Link>
                    </li>
                  ))}
                </ul>
                {canUpload && (
                  <div className="mt-2">
                    <FileUploader
                      accept=".pdf,.jpg,.jpeg,.png,.docx"
                      label="上传该项"
                      hint="PDF / JPG / PNG / DOCX，单文件不超过 20 MB"
                      onFile={(file, setProgress) => onUpload(file, item, setProgress)}
                    />
                  </div>
                )}
              </div>
            )
          })}
          {(g.unclassified || []).length > 0 && (
            <div className="alert alert-warning text-sm">
              <span>{g.unclassified.length} 份材料类型待确认，请在材料详情中指定类型。</span>
            </div>
          )}
        </section>
      ))}
    </div>
  )
}
