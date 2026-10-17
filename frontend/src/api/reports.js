import { api } from "./client"

export const listReports = (submissionId) => api.get(`/submissions/${submissionId}/reports`)
export const getReport = (id) => api.get(`/reports/${id}`)
export const completeness = (submissionId, params) => api.get(`/submissions/${submissionId}/completeness`, { params })
export const aiCheck = (submissionId, body) => api.post(`/submissions/${submissionId}/ai-check`, body || {})
export const batchAiCheck = (body) => api.post("/ai-check/batch", body)
export const completionNotices = (body) => api.post("/submissions/completion-notices", body)
export const getHandover = (reportId) => api.get(`/reports/${reportId}/handover`)
export const postHandover = (reportId, body) => api.post(`/reports/${reportId}/handover`, body)
