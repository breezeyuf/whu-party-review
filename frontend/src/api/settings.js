import { api } from "./client"

export const getSettings = () => api.get("/settings")
export const putSettings = (body) => api.put("/settings", body)
export const testAi = (body) => api.post("/settings/ai/test", body)
export const seedDemo = (body) => api.post("/admin/seed-demo", body)
export const testDelivery = () => api.post('/settings/delivery/test')
export const listExpiredMaterials = (params) => api.get('/settings/retention/materials',{params})
export const keepExpiredMaterial = (id,body) => api.post(`/settings/retention/materials/${id}/keep`,body)
