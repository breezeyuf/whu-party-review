import { api } from "./client"

export const listArchives = (params) => api.get("/archives", { params })
export const createArchive = (body) => api.post("/archives", body)
export const getArchive = (id) => api.get(`/archives/${id}`)
export const updateArchive = (id, body) => api.put(`/archives/${id}`, body)
export const getTimeline = (id) => api.get(`/archives/${id}/timeline`)
export const correctNode = (id, code, body) => api.put(`/archives/${id}/timeline/${code}`, body)
export const getHistory = (id, params) => api.get(`/archives/${id}/history`, { params })
export const myArchive = () => api.get("/my/archive")
