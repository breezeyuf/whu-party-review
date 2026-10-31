import { useEffect, useId, useRef, useState } from "react"
import { Bell, ChevronDown } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { markAllRead } from "../../api/messages"

export default function MessageQuickActions({ unread }) {
  const navigate = useNavigate(), id = useId(), root = useRef(null), timer = useRef(null), lock = useRef(false)
  const [open, setOpen] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState(""), [notice, setNotice] = useState("")
  const cancel = () => clearTimeout(timer.current)
  useEffect(() => () => clearTimeout(timer.current), [])
  useEffect(() => {
    if (!open) return
    const outside = (e) => { if (!root.current?.contains(e.target)) setOpen(false) }
    const escape = (e) => { if (e.key === "Escape") { cancel(); setOpen(false) } }
    document.addEventListener("pointerdown", outside)
    document.addEventListener("keydown", escape)
    return () => { document.removeEventListener("pointerdown", outside); document.removeEventListener("keydown", escape) }
  }, [open])
  const readAll = async () => {
    if (lock.current || !unread) return
    lock.current = true; setBusy(true); setError(""); setNotice("")
    try { await markAllRead(); setNotice("全部消息已标为已读") }
    catch (e) { setError(e.message || "标记失败，请重试") }
    finally { lock.current = false; setBusy(false) }
  }
  return <div ref={root} className="relative" onMouseEnter={() => { cancel(); setOpen(true) }} onMouseLeave={() => { cancel(); timer.current = setTimeout(() => setOpen(false), 180) }}
    onFocus={(e) => { cancel(); if (e.target.getAttribute("aria-label") !== "展开消息快捷操作") setOpen(true) }} onBlur={(e) => { if (!e.currentTarget.contains(e.relatedTarget)) setOpen(false) }}
    onKeyDown={(e) => { if (e.key === "Escape") { e.stopPropagation(); cancel(); setOpen(false) } }}>
    <div className="flex items-center">
      <button type="button" className="btn btn-ghost btn-sm" aria-label={`消息${unread ? `，${unread} 条未读` : ""}`} onClick={() => { setOpen(false); navigate("/messages") }}><Bell size={18}/><span className="hidden sm:inline">消息</span>{unread > 0 && <span className="badge badge-primary badge-xs">{unread > 99 ? "99+" : unread}</span>}</button>
      <button type="button" className="btn btn-ghost btn-xs" aria-label="展开消息快捷操作" aria-expanded={open} aria-controls={id} onClick={() => { cancel(); setOpen((value) => !value) }}><ChevronDown size={14}/></button>
    </div>
    {open && <div id={id} aria-label="消息快捷操作" className="absolute right-0 top-full z-50 w-64 max-w-[calc(100vw-2rem)] pt-2">
      <div className="rounded-lg border border-base-300 bg-base-100 p-3 shadow-lg">
        <p className="mb-2 text-sm">{unread ? `${unread} 条未读消息` : "暂无未读消息"}</p>
        <button type="button" className="btn btn-outline btn-sm w-full" disabled={busy || !unread} onClick={readAll}>{busy ? "正在标记…" : "全部标为已读"}</button>
        {notice && <p className="mt-2 text-xs text-success">{notice}</p>}
        {error && <p role="alert" className="mt-2 text-xs text-error">{error}</p>}
        <button type="button" className="btn btn-ghost btn-sm mt-2 w-full" onClick={() => { setOpen(false); navigate("/messages") }}>查看消息</button>
      </div>
    </div>}
    <span role="status" className="sr-only">{notice}</span>
  </div>
}
