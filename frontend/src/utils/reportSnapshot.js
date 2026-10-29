// Build a read-only view exclusively from the selected report's saved inputs.
export function reportMaterials(report, current = []) {
  return (report?.material_versions || []).map((v) => ({
    ...current.find((m) => String(m.id) === String(v.material_id)),
    id: v.material_id,
    title: current.find((m) => String(m.id) === String(v.material_id))?.title || `材料 ${v.material_id}`,
    current_version_id: v.version_id, version_no: v.version_no,
  }))
}

export function reportTimeline(report) {
  const snapshot = report?.timeline_snapshot || {}
  const inputs = snapshot.node_inputs || Object.fromEntries(Object.entries(snapshot.nodes || {}).map(([code, date]) => [code, { date }]))
  const issues = Object.values(report?.issues_by_category || {}).flat()
  return {
    nodes: Object.entries(inputs).map(([code, n]) => ({
      code, name: n.name || code, value_kind: n.value_kind || "DATE",
      effective: { date: n.date, end_date: n.end_date || n.end, hours: n.hours },
      has_conflict: n.has_conflict,
      sources: n.sources || [], items: (n.seq || []).map((date) => ({ date })),
      anomalies: issues.filter((i) => i.location?.node_code === code).map((i) => ({ issue_id: i.id, rule_code: i.rule_code, severity: i.severity, message: i.title })),
    })),
    derived: Object.entries(snapshot.derived || {}).map(([code, date]) => ({ code, name: code, date })),
  }
}
