import { useMemo, useState } from "react"
import { useMeta } from "../../context/MetaContext"
import { categoryName } from "../../utils/format"
import IssueCard from "./IssueCard"

const ORDER = { BLOCK: 0, WARN: 1, INFO: 2 }
const CATS = ["COMPLETENESS", "TIME", "FORMAT", "CONTENT"]
const priority = (issue) => (issue.review_status === "REJECTED" || issue.resolution === "RESOLVED" ? 10 : 0) + (ORDER[issue.severity] ?? 9)

export default function IssueList({ issues = [], activeId, onSelect, renderActions, renderFooter, readonlyNote, filtersDisabled = false }) {
  const meta = useMeta()
  const [cat, setCat] = useState("")
  const [sev, setSev] = useState("")
  const [status, setStatus] = useState("")

  const filtered = useMemo(() => {
    return [...issues]
      .filter((i) => !cat || i.category === cat)
      .filter((i) => !sev || i.severity === sev)
      .filter((i) => !status || i.review_status === status)
      .sort((a, b) => priority(a) - priority(b))
  }, [issues, cat, sev, status])

  const categories = [...new Set([...CATS, ...filtered.map((i) => i.category)])]
  const groups = categories.map((c) => ({ code: c, items: filtered.filter((i) => i.category === c) })).filter((g) => g.items.length)
    .sort((a, b) => Math.min(...a.items.map(priority)) - Math.min(...b.items.map(priority)))

  return (
    <div>
      <div className="issue-filters mb-3 flex flex-wrap gap-2">
        <select disabled={filtersDisabled} className="select select-bordered select-xs" value={cat} onChange={(e) => setCat(e.target.value)} aria-label="问题类别">
          <option value="">全部类别</option>
          {(meta.issue_categories || []).map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
        <select disabled={filtersDisabled} className="select select-bordered select-xs" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="人工确认状态">
          <option value="">全部确认状态</option>
          <option value="PENDING">待确认</option>
          <option value="CONFIRMED">已确认</option>
          <option value="MODIFIED">已修改确认</option>
          <option value="REJECTED">已驳回</option>
        </select>
        <select disabled={filtersDisabled} className="select select-bordered select-xs" value={sev} onChange={(e) => setSev(e.target.value)} aria-label="问题级别">
          <option value="">全部级别</option>
          {(meta.severities || []).map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
        <span className="text-xs text-base-content/50 self-center">{filtered.length} 条</span>
      </div>
      {readonlyNote && <p className="mb-2 text-xs text-base-content/55">{readonlyNote}</p>}
      {!groups.length && <p className="text-sm text-base-content/50">没有符合条件的问题。</p>}
      <div className="space-y-4">
        {groups.map((g) => (
          <section key={g.code}>
            <h3 className="mb-2 text-xs font-semibold tracking-wide text-base-content/50">{categoryName(meta, g.code)}</h3>
            <div className="space-y-2">
              {g.items.map((issue) => (
                <IssueCard
                  key={issue.id}
                  issue={issue}
                  active={String(activeId) === String(issue.id)}
                  onSelect={onSelect}
                  actions={renderActions?.(issue)}
                  footer={renderFooter?.(issue)}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
