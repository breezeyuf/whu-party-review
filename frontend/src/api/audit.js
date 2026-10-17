import { api } from "./client"

export const listAuditLogs = (params) => api.get("/audit-logs", { params })
