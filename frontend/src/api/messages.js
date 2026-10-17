import { api } from "./client"

export const listMessages = (params) => api.get("/messages", { params })
export const unreadCount = () => api.get("/messages/unread-count")
export const markRead = (id) => api.put(`/messages/${id}/read`)
export const markAllRead = () => api.put("/messages/read-all")
