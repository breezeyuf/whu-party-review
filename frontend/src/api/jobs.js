import { api } from "./client"

export const listJobs = (params) => api.get("/jobs", { params })
export const getJob = (id) => api.get(`/jobs/${id}`)
export const retryJob = (id) => api.post(`/jobs/${id}/retry`)

export const listJobCreators = (params) => api.get("/jobs/creators", { params })
