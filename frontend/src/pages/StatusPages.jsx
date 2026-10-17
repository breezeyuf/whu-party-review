import { Link } from "react-router-dom"

export function ForbiddenPage() {
  return (
    <div className="py-20 text-center">
      <div className="text-4xl font-semibold tracking-tight">403</div>
      <p className="mt-2 text-sm text-base-content/60">当前角色没有访问该页面的权限。</p>
      <Link to="/" className="btn btn-primary btn-sm mt-6">返回工作台</Link>
    </div>
  )
}

export function NotFoundPage() {
  return (
    <div className="py-20 text-center">
      <div className="text-4xl font-semibold tracking-tight">404</div>
      <p className="mt-2 text-sm text-base-content/60">页面不存在，或对象已不在你的数据范围内。</p>
      <Link to="/" className="btn btn-primary btn-sm mt-6">返回工作台</Link>
    </div>
  )
}
