import { api } from "./client"

export const listIssues = (submissionId, params) => api.get(`/submissions/${submissionId}/issues`, { params })
export const addIssue = (submissionId, body) => api.post(`/submissions/${submissionId}/issues`, body)
export const actIssue = (id, body) => api.put(`/issues/${id}`, body)
export const respondIssue = (id, body) => api.put(`/issues/${id}/response`, body)
