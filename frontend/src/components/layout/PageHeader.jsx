import { Link } from "react-router-dom"

export default function PageHeader({ title, crumbs = [], extra, children }) {
  return (
    <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {crumbs.length > 0 && (
          <div className="mb-1 flex flex-wrap items-center gap-1 text-xs text-base-content/50">
            {crumbs.map((c, i) => (
              <span key={c.label} className="flex items-center gap-1">
                {i > 0 && <span>/</span>}
                {c.to ? <Link className="link link-hover" to={c.to}>{c.label}</Link> : <span>{c.label}</span>}
              </span>
            ))}
          </div>
        )}
        <h1 className="page-title text-xl text-base-content">{title}</h1>
        {children && <p className="mt-1 text-sm text-base-content/60">{children}</p>}
      </div>
      {extra && <div className="flex flex-wrap items-center gap-2">{extra}</div>}
    </div>
  )
}
