import { createContext, useCallback, useContext, useMemo, useState } from "react"

const ToastContext = createContext(null)
let seq = 1

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const push = useCallback((message, type = "info") => {
    const id = seq++
    setToasts((list) => [...list, { id, message, type }])
    setTimeout(() => setToasts((list) => list.filter((t) => t.id !== id)), 4200)
  }, [])

  const api = useMemo(() => ({
    push,
    success: (m) => push(m, "success"),
    error: (m) => push(m, "error"),
    info: (m) => push(m, "info"),
  }), [push])

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast toast-end toast-bottom z-[80]">
        {toasts.map((t) => (
          <div key={t.id} className={`alert shadow-sm ${t.type === "error" ? "alert-error" : t.type === "success" ? "alert-success" : "alert-info"}`}>
            <span className="text-sm">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useToast outside provider")
  return ctx
}
