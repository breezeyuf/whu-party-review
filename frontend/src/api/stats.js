import { api, getBlob } from "./client"

export const dashboard = (params) => api.get("/dashboard", { params })
export const overview = (params) => api.get("/stats/overview", { params })
export const topIssues = (params) => api.get("/stats/top-issues", { params })
export const aiQuality = (params) => api.get("/stats/ai-quality", { params })
export const exportStats = (body) => api.post("/stats/export", body)
export const downloadExport = (id) => getBlob(`/exports/${id}/download`)
