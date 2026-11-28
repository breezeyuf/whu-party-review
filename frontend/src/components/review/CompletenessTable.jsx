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
            <tr><th scope="col">材料与要求</th><th scope="col" className="whitespace-nowrap">应交</th><th scope="col" className="whitespace-nowrap">实交</th><th scope="col" className="whitespace-nowrap">缺少</th></tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.checklist_item_id || it.material_type?.code || it.material_type} className={it.missing > 0 && it.required ? "bg-error/5" : ""}>
                <th scope="row" className="font-medium whitespace-normal [overflow-wrap:anywhere]">
                  <div>{it.material_type?.name || it.material_type}</div>
                  <div className="mt-1 text-xs font-normal text-base-content/65">
                    {it.required ? "必需" : "选交"}{it.requirement_text && ` · ${it.requirement_text}`}
                  </div>
                </th>
                <td className="mono whitespace-nowrap">{it.expected}</td>
                <td className="mono whitespace-nowrap">{it.actual}</td>
                <td className="mono whitespace-nowrap">{it.missing}</td>
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
