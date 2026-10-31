import { useId, useLayoutEffect, useRef } from "react"
import { Loading } from "./States"

function useModalDialog(open) {
  const ref = useRef(null)
  useLayoutEffect(() => {
    if (!open) return undefined
    const dialog = ref.current
    const opener = document.activeElement
    if (!dialog.open) dialog.showModal()
    return () => {
      if (dialog.open) dialog.close()
      if (opener?.isConnected) opener.focus({ preventScroll: true })
    }
  }, [open])
  return ref
}

// 按需加载的弹窗下载完成前显示的占位
export function ModalLoading() {
  const ref = useModalDialog(true)
  return (
    <dialog className="modal" ref={ref} aria-busy="true" aria-label="正在加载弹窗" onCancel={(event) => { event.preventDefault(); event.stopPropagation() }}>
      <div className="modal-box max-w-lg border border-base-300"><Loading /></div>
    </dialog>
  )
}

export function Modal({ open, title, onClose, children, footer, wide }) {
  const ref = useModalDialog(open)
  const titleId = useId()

  if (!open) return null
  return (
    <dialog className="modal" ref={ref} aria-labelledby={titleId}
      onCancel={(event) => {
        // 由页面的 onClose 决定是否关闭，保留保存/删除期间的关闭守卫。
        event.preventDefault()
        event.stopPropagation()
        onClose?.()
      }}
      onClose={(event) => {
        event.stopPropagation()
        // close 事件异步派发；忽略 StrictMode 清理后已重新打开的弹窗。
        if (!event.currentTarget.open) onClose?.()
      }}>
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
