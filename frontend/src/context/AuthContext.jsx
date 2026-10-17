import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import * as authApi from "../api/auth"
import { tokenStore } from "../api/client"

const AuthContext = createContext(null)

function roleKey(role) {
  if (!role) return ""
  return `${role.role}@${role.org_id ?? ""}`
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  const applyMe = useCallback((data) => {
    setUser(data)
    const active = data?.active_role
    if (active) tokenStore.setRole(roleKey(active))
  }, [])

  const refresh = useCallback(async () => {
    const data = await authApi.me()
    applyMe(data)
    return data
  }, [applyMe])

  useEffect(() => {
    if (!tokenStore.access) {
      setReady(true)
      return
    }
    refresh().catch(() => {
      tokenStore.clear()
      setUser(null)
    }).finally(() => setReady(true))
  }, [refresh])

  const login = useCallback(async (username, password) => {
    const data = await authApi.login(username, password)
    tokenStore.setTokens(data.access_token, data.refresh_token)
    const roles = data.user?.roles || []
    if (roles[0]) tokenStore.setRole(roleKey(roles[0]))
    const me = await refresh()
    return { ...data, me }
  }, [refresh])

  const logout = useCallback(async () => {
    try { await authApi.logout() } catch { /* ignore */ }
    tokenStore.clear()
    setUser(null)
  }, [])

  const switchRole = useCallback(async (role) => {
    tokenStore.setRole(roleKey(role))
    await refresh()
  }, [refresh])

  const value = useMemo(() => ({
    user,
    ready,
    activeRole: user?.active_role || null,
    roles: user?.roles || [],
    login,
    logout,
    refresh,
    switchRole,
  }), [user, ready, login, logout, refresh, switchRole])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth outside provider")
  return ctx
}
