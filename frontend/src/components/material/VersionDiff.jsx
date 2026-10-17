export default function VersionDiff({ diff }) {
  if (!diff) return <p className="text-sm text-base-content/50">选择两个版本后显示差异。</p>
  const stats = diff.stats || {}
  return (
    <div>
      <p className="mb-2 text-xs text-base-content/60">
        v{diff.from?.version_no} → v{diff.to?.version_no} · 新增 {stats.added || 0} · 删除 {stats.removed || 0} · 修改 {stats.changed || 0}
      </p>
      <div className="space-y-2">
        {(diff.hunks || []).filter((h) => h.op !== "equal").map((h, i) => (
          <div key={i} className="grid gap-2 text-xs sm:grid-cols-2">
            <pre className="whitespace-pre-wrap rounded border border-error/30 bg-error/5 p-2">{h.from_text || "（空）"}</pre>
            <pre className="whitespace-pre-wrap rounded border border-success/30 bg-success/5 p-2">{h.to_text || "（空）"}</pre>
          </div>
        ))}
        {(diff.hunks || []).every((h) => h.op === "equal") && <p className="text-sm text-base-content/50">两个版本文本一致。</p>}
      </div>
    </div>
  )
}
