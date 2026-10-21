import { useState } from "react"
import PageHeader from "../components/layout/PageHeader"
import { useAuth } from "../context/AuthContext"
import { changePassword } from "../api/auth"
import { useToast } from "../context/ToastContext"
import { roleName } from "../utils/format"
import { useMeta } from "../context/MetaContext"
import { activeOrganization } from "../utils/identity"

export default function ProfilePage() {
  const { user, activeRole, logout } = useAuth()
  const meta = useMeta()
  const toast = useToast()
  const [oldPassword, setOld] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const submit = async (e) => {
    e.preventDefault()
    setError("")
    try {
      await changePassword(oldPassword, password)
      toast.success("密码已修改，请重新登录")
      await logout()
      location.assign("/login")
    } catch (err) {
      setError(err.message || "修改失败")
    }
  }

  return (
    <div>
      <PageHeader title="个人中心" />
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="surface-card p-4 text-sm">
          <h2 className="mb-3 font-medium">账号信息</h2>
          <dl className="grid grid-cols-[6rem_1fr] gap-y-2">
            <dt className="text-base-content/50">姓名</dt><dd>{user?.real_name}</dd>
            <dt className="text-base-content/50">账号</dt><dd className="mono">{user?.username}</dd>
            <dt className="text-base-content/50">当前组织</dt><dd>{activeOrganization(user)}</dd>
            <dt className="text-base-content/50">当前身份</dt>
            <dd>{roleName(meta, activeRole?.role) || "—"}</dd>
          </dl>
        </section>
        <form className="surface-card space-y-3 p-4" onSubmit={submit}>
          <h2 className="font-medium">修改密码</h2>
          <input type="password" className="input input-bordered input-sm w-full" placeholder="当前密码" value={oldPassword} onChange={(e) => setOld(e.target.value)} required />
          <input type="password" className="input input-bordered input-sm w-full" placeholder="新密码（8 位以上，含字母和数字）" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-xs text-error">{error}</p>}
          <button className="btn btn-primary btn-sm" type="submit">保存</button>
        </form>
      </div>
    </div>
  )
}
