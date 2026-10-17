import { api } from "./client"

export const listSubmissions = (params) => api.get("/submissions", { params })
export const createSubmission = (archiveId, body) => api.post(`/archives/${archiveId}/submissions`, body || {})
export const getSubmission = (id) => api.get(`/submissions/${id}`)
export const submitSubmission = (id, body) => api.post(`/submissions/${id}/submit`, body || {})
export const reviewSubmission = (id, body) => api.post(`/submissions/${id}/review`, body)
export const batchReview = (body) => api.post("/submissions/batch-review", body)
export const fileSubmission = (id, body) => api.post(`/submissions/${id}/filing`, body || {})
export const reviewRecords = (id) => api.get(`/submissions/${id}/review-records`)
