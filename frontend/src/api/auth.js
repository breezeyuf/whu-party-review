import { api } from "./client"

export function login(username, password) {
  return api.post("/auth/login", { username, password })
}

export function logout() {
  return api.post("/auth/logout", {})
}

export function me() {
  return api.get("/auth/me")
}

export function changePassword(old_password, new_password) {
  return api.put("/auth/password", { old_password, new_password })
}

export function demoAccounts() {
  return api.get("/auth/demo-accounts")
}

export function health() {
  return api.get("/health")
}

export function authConfig() { return api.get("/auth/config") }
