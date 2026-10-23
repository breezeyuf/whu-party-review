export function canManageArchive(role) {
  return ["BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"].includes(role?.role)
}

export function availableBranches(orgs = [], role) {
  return orgs.filter((org) => {
    if (org.org_type !== "BRANCH" || org.is_active === false) return false
    if (role?.role === "BRANCH_REVIEWER") return Number(org.id) === Number(role.org_id)
    if (role?.role === "COLLEGE_REVIEWER") return Number(org.parent_id) === Number(role.org_id)
    return role?.role === "ORG_ADMIN"
  })
}

export function checklistProgress(data) {
  if (!data || !Array.isArray(data.items)) return null
  return data.items.filter((item) => item.required).reduce((total, item) => {
    const expected = Math.max(0, Number(item.expected) || 0)
    total.expected += expected
    total.actual += Math.min(expected, Math.max(0, Number(item.actual) || 0))
    return total
  }, { expected: 0, actual: 0 })
}

export function timelineSourceLink(source) {
  if (!source?.material_id) return null
  const params = new URLSearchParams()
  if (source.version_id) params.set("version_id", source.version_id)
  else if (source.version_no) params.set("version_no", source.version_no)
  if (source.page_no) params.set("page", source.page_no)
  if (Array.isArray(source.bbox) && source.bbox.length === 4 && source.bbox.every(Number.isFinite)) {
    params.set("bbox", JSON.stringify(source.bbox))
  }
  const query = params.toString()
  return `/materials/${source.material_id}${query ? `?${query}` : ""}`
}
