import { useEffect, useRef, useState } from "react"
import { listAuditActors } from "../../api/audit"
import { useRequest } from "../../hooks/useRequest"

export default function ActorPicker({ label, onChange }) {
  const [open, setOpen] = useState(false), [search, setSearch] = useState(""), [page, setPage] = useState(1)
  const ref = useRef(null)
  const req = useRequest(() => listAuditActors({ q: search, page, page_size: 20 }), [search, page], { immediate: open })
  useEffect(() => {
    if (!open) return
    const close = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    document.addEventListener("pointerdown", close)
    return () => document.removeEventListener("pointerdown", close)
  }, [open])
  return <section ref={ref} className="surface-card relative mb-3 p-3" aria-label="操作人筛选" onKeyDown={(e) => { if (e.key === "Escape") setOpen(false) }}>
    <div className="flex flex-wrap items-center gap-2"><span className="text-sm">操作人</span><button type="button" className="btn btn-outline btn-sm" aria-expanded={open} onClick={() => setOpen((v) => !v)}>{label || "选择操作人"}</button>{label && <button type="button" className="btn btn-ghost btn-sm" onClick={() => { onChange(null); setSearch(""); setPage(1) }}>清除操作人</button>}</div>
    {open && <div className="mt-3 max-w-lg space-y-2 rounded-lg border border-base-300 p-3">
      <input autoFocus aria-label="搜索操作人姓名或账号" className="input input-bordered input-sm w-full" value={search} placeholder="输入姓名或账号" onChange={(e) => { setSearch(e.target.value); setPage(1) }}/>
      {req.loading ? <p role="status" className="text-xs">正在查询操作人…</p> : req.error ? <p role="alert" className="text-xs text-error">{req.error.message}<button className="btn btn-ghost btn-xs" onClick={() => req.reload().catch(() => {})}>重试</button></p> : <>
        <ul className="max-h-60 overflow-y-auto">{(req.data?.items || []).map((person) => <li key={person.key}><button type="button" className="w-full rounded px-2 py-2 text-left text-sm hover:bg-base-200" onClick={() => { onChange(person); setOpen(false) }}>{person.name} · {person.username || "未知账号"}{person.user_id != null ? ` · #${person.user_id}` : " · 历史记录"}</button></li>)}</ul>
        {!req.data?.items?.length && <p className="text-xs">未找到操作人</p>}
        <div className="flex items-center gap-3 text-xs"><button className="btn btn-ghost btn-xs" disabled={page <= 1} onClick={() => setPage((v) => v-1)}>上一页操作人</button><span>第 {page} 页 · 共 {req.data?.total || 0} 人</span><button className="btn btn-ghost btn-xs" disabled={page * 20 >= (req.data?.total || 0)} onClick={() => setPage((v) => v+1)}>下一页操作人</button></div>
      </>}
    </div>}
  </section>
}
