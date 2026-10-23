import { useEffect, useState } from "react"
import { unreadCount, UNREAD_CHANGED } from "../api/messages"
import { useAuth } from "../context/AuthContext"

export function useUnreadCount(interval = 30000) {
  const { user, activeRole } = useAuth()
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!user) {
      setCount(0)
      return undefined
    }
    let alive = true
    let latestRequest = 0
    const load = () => {
      const requestId = ++latestRequest
      unreadCount().then((d) => {
        if (alive && requestId === latestRequest) setCount(d?.count || 0)
      }).catch(() => {})
    }
    load()
    const timer = setInterval(load, interval)
    window.addEventListener(UNREAD_CHANGED, load)
    return () => {
      alive = false
      clearInterval(timer)
      window.removeEventListener(UNREAD_CHANGED, load)
    }
  }, [user, activeRole?.role, activeRole?.org_id, interval])

  return count
}
