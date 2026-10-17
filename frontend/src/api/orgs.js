import { api } from "./client"

export const listOrgs = (params) => api.get("/orgs", { params })
export const createOrg = (body) => api.post("/orgs", body)
export const updateOrg = (id, body) => api.put(`/orgs/${id}`, body)
export const deleteOrg = (id) => api.delete(`/orgs/${id}`)
