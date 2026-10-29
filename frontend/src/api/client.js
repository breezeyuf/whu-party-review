import axios from "axios"

const ACCESS = "prw_access"
const REFRESH = "prw_refresh"
const ROLE = "prw_role"

export const tokenStore = {
  get role() { return localStorage.getItem(ROLE) || "" },
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

export const api = axios.create({ baseURL: "/api", timeout: 60000, withCredentials: true })

api.interceptors.request.use((config) => {
  // Upgrade cleanup: never read or send tokens from older versions.
  localStorage.removeItem(ACCESS)
  localStorage.removeItem(REFRESH)
  config.headers["X-Requested-With"] = "party-review"
  const role = tokenStore.role
  if (role) config.headers["X-Active-Role"] = role
  return config
})

let redirecting = false

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
    redirecting = false
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
    if (res?.status === 401) {
      tokenStore.clear()
      if (!reqUrl.startsWith("/auth/") && !location.pathname.startsWith("/login") && !redirecting) {
        redirecting = true
        location.assign("/login")
      }
      return Promise.reject(toError(payload, 401))
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
