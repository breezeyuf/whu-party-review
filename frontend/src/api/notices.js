import { api, getBlob } from "./client"

export const listNotices = (params) => api.get("/notices", { params })
export const getNotice = (id) => api.get(`/notices/${id}`)
export const exportNotice = (id, format) => getBlob(`/notices/${id}/export`, { format })
export const sendNotice = (id) => api.post(`/notices/${id}/send`)
export const rectificationNotice = (submissionId, body) =>
  api.post(`/submissions/${submissionId}/rectification-notice`, body || {})
