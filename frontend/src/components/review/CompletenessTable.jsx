export default function CompletenessTable({ data }) {
  const items = data?.items || []
  if (!data) return <p className="text-sm text-base-content/50">暂无完整性比对结果。</p>
  return (
    <div>
      <div className="mb-2 text-sm">
        {data.is_complete ? <span className="text-success">材料齐全</span> : <span className="text-error">缺少 {data.missing_total ?? "若干"} 项</span>}
      </div>
      <div className="overflow-x-auto">
        <table className="table table-sm">
          <thead>
            <tr><th>材料</th><th>必需</th><th>应交</th><th>实交</th><th>缺少</th><th>要求</th></tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.checklist_item_id || it.material_type?.code || it.material_type} className={it.missing > 0 && it.required ? "bg-error/5" : ""}>
                <td className="min-w-28">{it.material_type?.name || it.material_type}</td>
                <td>{it.required ? "是" : "否"}</td>
                <td className="mono">{it.expected}</td>
                <td className="mono">{it.actual}</td>
                <td className="mono">{it.missing}</td>
                <td className="text-xs text-base-content/60">{it.requirement_text || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {(data.extra || []).length > 0 && (
        <p className="mt-2 text-xs text-base-content/60">多余材料：{data.extra.map((e) => e.title || e.reason).join("、")}</p>
      )}
      {(data.unclassified || []).length > 0 && (
        <p className="mt-1 text-xs text-warning">待确认类型：{data.unclassified.length} 份</p>
      )}
    </div>
  )
}
