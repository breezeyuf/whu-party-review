import { api } from "./client"

export const getSettings = () => api.get("/settings")
export const putSettings = (body) => api.put("/settings", body)
export const testAi = (body) => api.post("/settings/ai/test", body)
export const seedDemo = (body) => api.post("/admin/seed-demo", body)
