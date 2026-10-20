import { Link } from "react-router-dom"
import FileUploader from "../common/FileUploader"
import { fmtDateTime } from "../../utils/format"

function MaterialRows({ materials, onPreview }) {
  return <ul className="mt-2 divide-y divide-base-200">{materials.map((material) => <li key={material.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
    <div>
      {onPreview ? <button type="button" className="link" onClick={() => onPreview(material)}>{material.title || `材料 #${material.id}`}</button> : <Link className="link" to={`/materials/${material.id}`}>{material.title || `材料 #${material.id}`}</Link>}
      {["NEEDS_CONFIRM", "PENDING"].includes(material.type_status) && <span className="badge badge-warning badge-xs ml-2">待确认类型</span>}
      <div className="text-xs text-base-content/50">
        v{material.current_version?.version_no || 1} · {material.current_version?.parse_status || "待解析"} · {fmtDateTime(material.current_version?.uploaded_at)}
        {material.open_issue_count ? ` · 问题 ${material.open_issue_count}` : ""}
      </div>
    </div>
    <Link className="btn btn-ghost btn-xs" to={`/materials/${material.id}`}>详情</Link>
  </li>)}</ul>
}

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
                <MaterialRows materials={item.materials || []} onPreview={onPreview} />
                {canUpload && (
                  <div className="mt-2">
                    <FileUploader
                      compact
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
            <div className="surface-card border-warning/50 p-3">
              <h3 className="text-sm font-medium">未分类材料（{g.unclassified.length}）</h3>
              <p className="mt-1 text-xs text-warning">请打开材料详情核对类型，确认后会归入对应清单。</p>
              <MaterialRows materials={g.unclassified} onPreview={onPreview} />
            </div>
          )}
          {(g.extra || []).length > 0 && <div className="surface-card p-3">
            <h3 className="text-sm font-medium">其他材料（{g.extra.length}）</h3>
            <p className="mt-1 text-xs text-base-content/55">这些材料不属于当前清单，不计入必需材料完成率。</p>
            <MaterialRows materials={g.extra} onPreview={onPreview} />
          </div>}
        </section>
      ))}
    </div>
  )
}
