import { api, getBlob } from "./client"

const crud = (path) => ({
  list: (params) => api.get(path, { params }),
  create: (body) => api.post(path, body),
  update: (id, body) => api.put(`${path}/${id}`, body),
  remove: (id) => api.delete(`${path}/${id}`),
})

export const checklists = crud("/rules/checklists")
export const materialTypes = crud("/rules/material-types")
export const timeNodes = {
  list: (params) => api.get("/rules/time-nodes", { params }),
  create: (body) => api.post("/rules/time-nodes", body),
  update: (id, body) => api.put(`/rules/time-nodes/${id}`, body),
}
export const timeRules = crud("/rules/time-rules")
export const checkRules = crud("/rules/check-rules")
export const terms = crud("/rules/terms")
export const sensitivePhrases = crud("/rules/sensitive-phrases")
export const suggestionTemplates = crud("/rules/suggestion-templates")
export const promptTemplates = {
  list: (params) => api.get("/rules/prompt-templates", { params }),
  create: (body) => api.post("/rules/prompt-templates", body),
  update: (id, body) => api.put(`/rules/prompt-templates/${id}`, body),
}

export const ruleVersions = (params) => api.get("/rules/versions", { params })
export const ruleVersion = (id, params) => api.get(`/rules/versions/${id}`, { params })
export const dryRun = (body) => api.post("/rules/dry-run", body)

export function importRules(kind, file, { mode = "upsert", dryRun: preview = true } = {}) {
  const fd = new FormData()
  fd.append("file", file)
  fd.append("mode", mode)
  fd.append("dry_run", preview ? "true" : "false")
  return api.post(`/rules/${kind}/import`, fd)
}

export const exportRules = (kind) => getBlob(`/rules/${kind}/export`)
