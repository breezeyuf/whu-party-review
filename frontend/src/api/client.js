import axios from "axios"

const ACCESS = "prw_access"
const REFRESH = "prw_refresh"
const ROLE = "prw_role"

export const tokenStore = {
  get access() { return localStorage.getItem(ACCESS) || "" },
  get refresh() { return localStorage.getItem(REFRESH) || "" },
  get role() { return localStorage.getItem(ROLE) || "" },
  setTokens(access, refresh) {
    if (access) localStorage.setItem(ACCESS, access)
    if (refresh) localStorage.setItem(REFRESH, refresh)
  },
  setRole(value) {
    if (value) localStorage.setItem(ROLE, value)
    else localStorage.removeItem(ROLE)
  },
  clear() {
    localStorage.removeItem(ACCESS)
    localStorage.removeItem(REFRESH)
    localStorage.removeItem(ROLE)
  },
}

export const api = axios.create({ baseURL: "/api", timeout: 60000 })

api.interceptors.request.use((config) => {
  const token = tokenStore.access
  if (token) config.headers.Authorization = `Bearer ${token}`
  const role = tokenStore.role
  if (role) config.headers["X-Active-Role"] = role
  return config
})

let refreshing = null

function toError(payload, status) {
  const err = new Error(payload?.message || "请求失败")
  err.code = payload?.code
  err.status = status
  err.data = payload?.data
  return err
}

api.interceptors.response.use(
  (res) => {
    if (res.config.responseType === "blob" || res.config.raw) return res
    const body = res.data
    if (body && typeof body === "object" && "code" in body) {
      if (body.code === 0) return body.data
      return Promise.reject(toError(body, res.status))
    }
    return body
  },
  async (error) => {
    const res = error.response
    const original = error.config || {}
    const payload = res?.data
    const reqUrl = String(original.url || "")
    const noRefresh = reqUrl.includes("/auth/login") || reqUrl.includes("/auth/refresh")
    if (res?.status === 401 && !original._retry && !noRefresh) {
      original._retry = true
      const current = tokenStore.access
      if (current && original.headers?.Authorization !== `Bearer ${current}`) {
        original.headers.Authorization = `Bearer ${current}`
        return api(original)
      }
      const refresh = tokenStore.refresh
      if (!refresh) {
        tokenStore.clear()
        if (!location.pathname.startsWith("/login")) location.assign("/login")
        return Promise.reject(toError(payload, 401))
      }
      if (!refreshing) {
        refreshing = api.post("/auth/refresh", { refresh_token: refresh }, { _retry: true })
          .then((data) => {
            tokenStore.setTokens(data.access_token, data.refresh_token)
            return data.access_token
          })
          .catch((e) => {
            tokenStore.clear()
            if (!location.pathname.startsWith("/login")) location.assign("/login")
            throw e
          })
          .finally(() => { refreshing = null })
      }
      const token = await refreshing
      original.headers.Authorization = `Bearer ${token}`
      return api(original)
    }
    if (res?.status === 403 && payload?.code === 40301 && !location.pathname.startsWith("/change-password")) {
      location.assign("/change-password")
    }
    if (payload && typeof payload === "object" && "code" in payload) {
      return Promise.reject(toError(payload, res.status))
    }
    if (res?.data instanceof Blob) {
      try {
        const text = await res.data.text()
        const json = JSON.parse(text)
        return Promise.reject(toError(json, res.status))
      } catch { /* keep original */ }
    }
    const err = new Error(error.message || "网络错误")
    err.status = res?.status
    return Promise.reject(err)
  },
)

export async function getBlob(url, params) {
  const res = await api.get(url, { params, responseType: "blob", raw: true })
  const disp = res.headers["content-disposition"] || ""
  let filename = "download"
  const m = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(disp)
  if (m) filename = decodeURIComponent(m[1] || m[2])
  return { blob: res.data, filename, headers: res.headers }
}

export function saveBlob({ blob, filename }) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename || "download"
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1500)
}
