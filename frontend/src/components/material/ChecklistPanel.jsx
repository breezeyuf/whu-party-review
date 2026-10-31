import { Link } from "react-router-dom"
import FileUploader from "../common/FileUploader"
import { fmtDateTime } from "../../utils/format"

function ParseStatus({ code }) {
  const labels = { PENDING: "等待解析", RUNNING: "解析中", DONE: "解析完成", FAILED: "解析失败" }
  const styles = { PENDING: "badge-ghost", RUNNING: "badge-info", DONE: "badge-success", FAILED: "badge-error" }
  return <span className={`badge badge-xs ${styles[code] || "badge-ghost"}`}>{labels[code] || code || "等待解析"}</span>
}

function MaterialRows({ materials, onPreview, onDelete, canUpload, uploadDisabled }) {
  return <ul className="mt-2 divide-y divide-base-200">{materials.map((material) => <li key={material.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
    <div className="min-w-0 flex-1 break-words">
      {onPreview ? <button type="button" className="link" onClick={() => onPreview(material)}>{material.title || `材料 #${material.id}`}</button> : <Link className="link" to={`/materials/${material.id}`}>{material.title || `材料 #${material.id}`}</Link>}
      {["NEEDS_CONFIRM", "PENDING"].includes(material.type_status) && <span className="badge badge-warning badge-xs ml-2">待确认类型</span>}
      <div className="mt-0.5 text-xs text-base-content/50">
        v{material.current_version?.version_no || 1} · <ParseStatus code={material.current_version?.parse_status} /> · {fmtDateTime(material.current_version?.uploaded_at)}
        {material.open_issue_count ? ` · 问题 ${material.open_issue_count}` : ""}
      </div>
    </div>
    <div className="flex shrink-0 items-center gap-2"><Link className="btn btn-outline btn-sm" to={`/materials/${material.id}`}>详情</Link>{canUpload && onDelete && <button type="button" className="btn btn-outline btn-sm text-error" disabled={uploadDisabled} onClick={() => onDelete(material)}>删除</button>}</div>
  </li>)}</ul>
}

export default function ChecklistPanel({ groups = [], canUpload, uploadDisabled, filter = "all", onUpload, onPreview, onDelete }) {
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
                <MaterialRows materials={item.materials || []} onPreview={onPreview} onDelete={onDelete} canUpload={canUpload} uploadDisabled={uploadDisabled} />
                {canUpload && (
                  <div className="mt-2">
                    <FileUploader
                      compact
                      buttonClassName="btn-outline"
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
            <div className="surface-card border-warning/50 p-3">
              <h3 className="text-sm font-medium">未分类材料（{g.unclassified.length}）</h3>
              <p className="mt-1 text-xs text-warning">请打开材料详情核对类型，确认后会归入对应清单。</p>
              <MaterialRows materials={g.unclassified} onPreview={onPreview} onDelete={onDelete} canUpload={canUpload} uploadDisabled={uploadDisabled} />
            </div>
          )}
          {(g.extra || []).length > 0 && <div className="surface-card p-3">
            <h3 className="text-sm font-medium">其他材料（{g.extra.length}）</h3>
            <p className="mt-1 text-xs text-base-content/55">这些材料不属于当前清单，不计入必需材料完成率。</p>
            <MaterialRows materials={g.extra} onPreview={onPreview} onDelete={onDelete} canUpload={canUpload} uploadDisabled={uploadDisabled} />
          </div>}
        </section>
      ))}
    </div>
  )
}

