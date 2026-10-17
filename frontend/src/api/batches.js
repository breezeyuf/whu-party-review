import { api } from "./client"

export const listBatches = (params) => api.get("/batches", { params })
export const createBatch = (body) => api.post("/batches", body)
export const getBatch = (id) => api.get(`/batches/${id}`)
export const updateBatch = (id, body) => api.put(`/batches/${id}`, body)
export const deleteBatch = (id) => api.delete(`/batches/${id}`)
export const getCrossPairs = (id, params) => api.get(`/batches/${id}/cross-review-pairs`, { params })
export const setCrossPairs = (id, body) => api.put(`/batches/${id}/cross-review-pairs`, body)
