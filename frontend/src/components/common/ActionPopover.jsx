import { useEffect, useId, useRef, useState } from "react"

export default function ActionPopover({ label = "更多操作", children }) {
  const [open, setOpen] = useState(false)
  const root = useRef(null), trigger = useRef(null)
  const id = useId()
  useEffect(() => {
    if (!open) return
    const outside = e => { if (!root.current?.contains(e.target)) setOpen(false) }
    const escape = e => { if (e.key === "Escape") { e.preventDefault(); setOpen(false); trigger.current?.focus() } }
    document.addEventListener("pointerdown", outside)
    document.addEventListener("keydown", escape)
    return () => { document.removeEventListener("pointerdown", outside); document.removeEventListener("keydown", escape) }
  }, [open])
  return <div className="action-popover" ref={root}>
    <button ref={trigger} type="button" className="btn btn-ghost btn-sm" aria-expanded={open} aria-controls={id} onClick={() => setOpen(v => !v)}>{label}</button>
    {open && <div id={id} className="action-popover-panel" aria-label={label} onClick={e => { if (e.target.closest("button,a")) { setOpen(false); trigger.current?.focus() } }}>{children}</div>}
  </div>
}
