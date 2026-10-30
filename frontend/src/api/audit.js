import { api } from "./client"

export const listAuditLogs = (params) => api.get("/audit-logs", { params })

export const listAuditActors = (params) => api.get("/audit-logs/actors", { params })
