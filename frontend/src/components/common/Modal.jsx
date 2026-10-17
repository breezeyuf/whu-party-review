import { useEffect, useId, useRef } from "react"

export function Modal({ open, title, onClose, children, footer, wide }) {
  const ref = useRef(null)
  const titleId = useId()

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => { if (e.key === "Escape") onClose?.() }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [open, onClose])

  if (!open) return null
  return (
    <dialog className="modal modal-open" ref={ref} aria-labelledby={titleId}>
      <div className={`modal-box border border-base-300 ${wide ? "max-w-3xl" : "max-w-lg"}`}>
        <h3 id={titleId} className="text-base font-semibold">{title}</h3>
        <div className="py-4">{children}</div>
        {footer && <div className="modal-action mt-2">{footer}</div>}
      </div>
      <form method="dialog" className="modal-backdrop">
        <button type="button" aria-label="关闭" onClick={onClose}>close</button>
      </form>
    </dialog>
  )
}

export function ConfirmDialog({ open, title = "确认操作", message, confirmText = "确认", danger, busy, onConfirm, onClose }) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onClose}
      footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>取消</button>
          <button type="button" className={`btn btn-sm ${danger ? "btn-error" : "btn-primary"}`} disabled={busy} onClick={onConfirm}>
            {busy ? <span className="loading loading-spinner loading-xs" /> : null}
            {confirmText}
          </button>
        </>
      )}
    >
      <p className="text-sm text-base-content/80">{message}</p>
    </Modal>
  )
}
