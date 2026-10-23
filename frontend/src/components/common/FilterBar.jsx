import { useMeta } from "../../context/MetaContext"
import { countActiveFilters } from "../../utils/workbench"

export default function FilterBar({ fields, advancedFields = [], values, onChange, onReset }) {
  const meta = useMeta()
  const advancedCount = countActiveFilters(values, advancedFields.map((field) => field.key))
  const renderField = (field) => {
    const options = field.options || (field.metaKey ? meta[field.metaKey] : null)
    return <label key={field.key} className="form-control w-full sm:w-auto">
      <span className="label-text mb-1 text-xs text-base-content/70">{field.label}</span>
      {field.type === "select" ? <select className="select select-bordered select-sm w-full sm:w-40" value={values[field.key] ?? ""} onChange={(event) => onChange({ [field.key]: event.target.value })}>
        <option value="">{field.placeholder || "全部"}</option>
        {(options || []).map((option) => <option key={option.code ?? option.id ?? option.value} value={option.code ?? option.id ?? option.value}>{option.name || option.label}</option>)}
      </select> : <input className="input input-bordered input-sm w-full sm:w-44" placeholder={field.placeholder || ""} value={values[field.key] ?? ""} onChange={(event) => onChange({ [field.key]: event.target.value })} />}
    </label>
  }
  return <div className="service-filter-panel">
    <div className="service-filter-fields">{fields.map(renderField)}{onReset && <button type="button" className="btn btn-ghost btn-sm" onClick={onReset}>重置</button>}</div>
    {advancedFields.length > 0 && <details className="service-inline-details" open={advancedCount > 0 ? true : undefined}><summary>更多筛选{advancedCount > 0 ? `（已启用 ${advancedCount} 项）` : ""}</summary><div className="details-content service-filter-fields">{advancedFields.map(renderField)}</div></details>}
  </div>
}
