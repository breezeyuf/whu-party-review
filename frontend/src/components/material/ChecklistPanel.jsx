import { Link } from "react-router-dom"
import FileUploader from "../common/FileUploader"
import { fmtDateTime } from "../../utils/format"

export default function ChecklistPanel({ groups = [], canUpload, uploadDisabled, filter = "all", onUpload, onPreview }) {
  if (!groups.length) {
    return <p className="text-sm text-base-content/50">当前阶段还没有材料清单。请先完成档案创建，或联系组织部配置规则。</p>
  }
  const hasChecklist = groups.some((group) => (group.checklist || []).length > 0)
  const visibleCount = groups.reduce((count, group) => count + (group.checklist || []).filter((item) => {
    if (filter === "missing") return Number(item.missing_count) > 0
    if (filter === "uploaded") return Number(item.actual_count) > 0
    return true
  }).length, 0)
  const hasUnclassified = groups.some((group) => (group.unclassified || []).length > 0)
  return (
    <div className="space-y-4">
      {!hasChecklist && <div className="alert alert-info text-sm">当前阶段暂未配置材料清单。已上传材料仍显示在下方。</div>}
      {filter !== "all" && visibleCount === 0 && !hasUnclassified && (
        <div className="surface-card p-4 text-sm text-base-content/60">
          {filter === "missing" ? "当前没有待补的清单材料。" : "当前筛选下还没有已上传的清单材料。"}
        </div>
      )}
      {groups.map((g) => (
        <section key={g.stage_code} className="space-y-3">
          {(g.checklist || []).filter((item) => {
            if (filter === "missing") return Number(item.missing_count) > 0
            if (filter === "uploaded") return Number(item.actual_count) > 0
            return true
          }).map((item) => {
            const missing = item.missing_count > 0
            return (
              <div key={item.checklist_item_id || item.material_type?.id} className="surface-card border-primary/15 bg-gradient-to-br from-base-100 via-base-100 to-primary/5 p-3 transition-colors hover:border-primary/30 sm:p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <div className="inline-flex flex-wrap items-center gap-x-2 gap-y-1 rounded-lg bg-primary/5 px-2.5 py-1.5 text-sm">
                      {item.material_type?.name || item.material_type}
                      {item.required && <span className="badge badge-outline badge-xs">必需</span>}
                      {missing && <span className="badge badge-error badge-xs">缺 {item.missing_count}</span>}
                    </div>
                    <div className="mono mt-2 text-xs text-base-content/60">
                      应交 {item.expected_count ?? "—"} · 已交 {item.actual_count ?? 0}
                    </div>
                    {item.requirement_text && <p className="mt-1 text-xs leading-relaxed text-base-content/60">{item.requirement_text}</p>}
                  </div>
                </div>
                <ul className="mt-3 space-y-1.5">
                  {(item.materials || []).map((m) => (
                    <li key={m.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-base-300/60 bg-base-100/80 px-2.5 py-2 text-sm sm:px-3">
                      <div className="min-w-0">
                        <button type="button" className="link break-all text-left" onClick={() => onPreview?.(m)}>{m.title || `材料 #${m.id}`}</button>
                        {m.type_status === "NEEDS_CONFIRM" && <span className="badge badge-warning badge-xs ml-2">待确认类型</span>}
                        <div className="mt-0.5 text-xs text-base-content/55">
                          v{m.current_version?.version_no || 1} · <ParseStatus code={m.current_version?.parse_status} /> · {fmtDateTime(m.current_version?.uploaded_at)}
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
                      disabled={uploadDisabled}
                      onFile={(file, setProgress) => onUpload(file, item, setProgress)}
                    />
                  </div>
                )}
              </div>
            )
          })}
          {(g.unclassified || []).length > 0 && (
            <div className="surface-card p-3">
              <h3 className="mb-2 text-sm font-medium">待确认类型（{g.unclassified.length}）</h3>
              <p className="mb-2 text-xs text-warning">系统暂未识别这些材料的类型，请打开详情确认。</p>
              <MaterialRows materials={g.unclassified} onPreview={onPreview} />
            </div>
          )}
          {filter !== "missing" && (g.extra || []).length > 0 && (
            <div className="surface-card p-3">
              <h3 className="mb-2 text-sm font-medium">清单外材料（{g.extra.length}）</h3>
              <MaterialRows materials={g.extra} onPreview={onPreview} />
            </div>
          )}
        </section>
      ))}
    </div>
  )
}

function ParseStatus({ code }) {
  const labels = { PENDING: "等待解析", RUNNING: "解析中", DONE: "解析完成", FAILED: "解析失败" }
  const styles = { PENDING: "badge-ghost", RUNNING: "badge-info", DONE: "badge-success", FAILED: "badge-error" }
  return <span className={`badge badge-xs ${styles[code] || "badge-ghost"}`}>{labels[code] || code || "等待解析"}</span>
}

function MaterialRows({ materials, onPreview }) {
  return (
    <ul className="divide-y divide-base-200">
      {materials.map((material) => (
        <li key={material.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
          <div>
            <button type="button" className="link" onClick={() => onPreview?.(material)}>
              {material.title || `材料 #${material.id}`}
            </button>
            <div className="text-xs text-base-content/50">
              {material.type_status === "NEEDS_CONFIRM" ? "类型待确认" : "类型已识别"} · v{material.current_version?.version_no || 1} · <ParseStatus code={material.current_version?.parse_status} /> · {fmtDateTime(material.current_version?.uploaded_at)}
            </div>
          </div>
          <Link className="btn btn-ghost btn-xs" to={`/materials/${material.id}`}>详情</Link>
        </li>
      ))}
    </ul>
  )
}
