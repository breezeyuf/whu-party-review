import { useEffect, useState } from "react"
import { unreadCount } from "../api/messages"
import { useAuth } from "../context/AuthContext"

export function useUnreadCount(interval = 30000) {
  const { user } = useAuth()
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!user) return undefined
    let alive = true
    const load = () => {
      unreadCount().then((d) => { if (alive) setCount(d?.count || 0) }).catch(() => {})
    }
    load()
    const timer = setInterval(load, interval)
    return () => {
      alive = false
      clearInterval(timer)
    }
  }, [user, interval])

  return count
}
