import { useEffect } from "react"
import { isRouteErrorResponse, useRouteError } from "react-router-dom"
import { isChunkLoadError, resetFailedLazy } from "../../utils/lazyLoad"

function reasonOf(error) {
  if (isRouteErrorResponse(error)) return [error.status, error.statusText].filter(Boolean).join(" ")
  return error?.message || (typeof error === "string" ? error : "")
}

// 路由级错误页：代替 React Router 默认的英文错误页。fullPage 用于登录页等外壳以外的页面
export default function RouteError({ fullPage = false }) {
  const error = useRouteError()
  const chunk = isChunkLoadError(error)
  const reason = reasonOf(error)

  // 错误已经展示，失败的页面组件换成新实例，离开再回来时会重新下载
  useEffect(() => { resetFailedLazy() }, [error])

  const panel = (
    <div role="alert" className="surface-card mx-auto max-w-lg space-y-3 p-6 text-center">
      <h1 className="text-lg font-semibold">{chunk ? "页面文件下载失败" : "页面出现错误"}</h1>
      <p className="text-sm text-base-content/70">
        {chunk ? "可能是网络中断或系统刚刚更新。重新加载会获取最新的页面文件，登录状态不受影响。" : "请重新加载页面；问题仍然存在时，请联系管理员并说明操作步骤。"}
      </p>
      {reason && <p className="break-all text-xs text-base-content/55">原因：{reason}</p>}
      <button type="button" className="btn btn-primary btn-sm" onClick={() => window.location.reload()}>重新加载</button>
    </div>
  )
  if (!fullPage) return <div className="py-12">{panel}</div>
  return <div className="flex min-h-screen items-center justify-center bg-base-200 px-4 py-10">{panel}</div>
}
