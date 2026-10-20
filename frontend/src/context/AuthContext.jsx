import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import * as authApi from "../api/auth"
import { tokenStore } from "../api/client"
import { identityFor, roleKey } from "../utils/identity"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)
  const [needsIdentitySelection, setNeedsIdentitySelection] = useState(false)

  const applyMe = useCallback((data, selectedRole) => {
    const roles = data?.roles || []
    if (!roles.some((role) => roleKey(role) === roleKey(data?.active_role))) {
      throw new Error("账号身份信息异常，请联系管理员")
    }
    if (selectedRole && roleKey(data.active_role) !== selectedRole) {
      throw new Error("身份验证失败，请重新登录")
    }
    const needsSelection = roles.length > 1 && !selectedRole
    setUser(data)
    setNeedsIdentitySelection(needsSelection)
    // An empty role preserves the choice screen across a browser reload.
    tokenStore.setRole(needsSelection ? "" : roleKey(data.active_role))
    return needsSelection
  }, [])

  const refresh = useCallback(async () => {
    const selectedRole = tokenStore.role
    const data = await authApi.me()
    applyMe(data, selectedRole)
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
    // A previous account's role must never become the new account's identity.
    tokenStore.clear()
    tokenStore.setTokens(data.access_token, data.refresh_token)
    try {
      const me = await refresh()
      return { ...data, me, needsIdentitySelection: (me.roles || []).length > 1 }
    } catch (error) {
      tokenStore.clear()
      setUser(null)
      setNeedsIdentitySelection(false)
      throw error
    }
  }, [refresh])

  const logout = useCallback(async () => {
    try { await authApi.logout() } catch { /* ignore */ }
    tokenStore.clear()
    setUser(null)
    setNeedsIdentitySelection(false)
  }, [])

  const switchRole = useCallback(async (role) => {
    if (!identityFor(role) || !user?.roles?.some((owned) => roleKey(owned) === roleKey(role))) {
      throw new Error("该账号没有此身份的权限")
    }
    const previousRole = tokenStore.role
    tokenStore.setRole(roleKey(role))
    try { return await refresh() }
    catch (error) { tokenStore.setRole(previousRole); throw error }
  }, [refresh, user])

  const value = useMemo(() => ({
    user,
    ready,
    activeRole: user?.active_role || null,
    roles: user?.roles || [],
    needsIdentitySelection,
    login,
    logout,
    refresh,
    switchRole,
  }), [user, ready, needsIdentitySelection, login, logout, refresh, switchRole])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth outside provider")
  return ctx
}
