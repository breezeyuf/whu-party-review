import { useMeta } from "../../context/MetaContext"

export default function FilterBar({ fields, values, onChange, onReset }) {
  const meta = useMeta()
  return (
    <div className="surface-card mb-4 flex flex-wrap items-end gap-3 p-3">
      {fields.map((f) => {
        const options = f.options || (f.metaKey ? meta[f.metaKey] : null)
        return (
          <label key={f.key} className="form-control w-full sm:w-auto">
            <span className="label-text mb-1 text-xs text-base-content/60">{f.label}</span>
            {f.type === "select" ? (
              <select
                className="select select-bordered select-sm w-full sm:w-40"
                value={values[f.key] ?? ""}
                onChange={(e) => onChange({ [f.key]: e.target.value })}
              >
                <option value="">{f.placeholder || "全部"}</option>
                {(options || []).map((o) => (
                  <option key={o.code ?? o.id ?? o.value} value={o.code ?? o.id ?? o.value}>{o.name || o.label}</option>
                ))}
              </select>
            ) : (
              <input
                className="input input-bordered input-sm w-full sm:w-44"
                placeholder={f.placeholder || ""}
                value={values[f.key] ?? ""}
                onChange={(e) => onChange({ [f.key]: e.target.value })}
              />
            )}
          </label>
        )
      })}
      {onReset && (
        <button type="button" className="btn btn-ghost btn-sm" onClick={onReset}>重置</button>
      )}
    </div>
  )
}
