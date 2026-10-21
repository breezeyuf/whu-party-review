import { api } from "./client"

export const listMessages = (params) => api.get("/messages", { params })
export const unreadCount = () => api.get("/messages/unread-count")

const UNREAD_CHANGED = "party-review:unread-changed"
const notifyUnreadChanged = () => window.dispatchEvent(new Event(UNREAD_CHANGED))

export const markRead = async (id) => {
  const result = await api.put(`/messages/${id}/read`)
  notifyUnreadChanged()
  return result
}

export const markAllRead = async () => {
  const result = await api.put("/messages/read-all")
  notifyUnreadChanged()
  return result
}

export { UNREAD_CHANGED }
