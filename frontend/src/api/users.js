import { api, getBlob } from "./client"

export const listUsers = (params) => api.get("/users", { params })
export const createUser = (body) => api.post("/users", body)
export const getUser = (id) => api.get(`/users/${id}`)
export const updateUser = (id, body) => api.put(`/users/${id}`, body)
export const resetPassword = (id) => api.post(`/users/${id}/reset-password`, {})

export function importUsers(file, { dryRun = true, batchId } = {}) {
  const fd = new FormData()
  fd.append("file", file)
  fd.append("dry_run", dryRun ? "true" : "false")
  if (batchId) fd.append("batch_id", String(batchId))
  return api.post("/users/import", fd)
}

export const importTemplate = () => getBlob("/users/import-template")
export const downloadImportPasswords = (id) => getBlob(`/users/import-passwords/${id}/download`)
