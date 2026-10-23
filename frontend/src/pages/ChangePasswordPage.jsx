import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { changePassword } from "../api/auth"
import { useAuth } from "../context/AuthContext"
import { useToast } from "../context/ToastContext"

export default function ChangePasswordPage() {
  const { logout } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [oldPassword, setOld] = useState("")
  const [password, setPassword] = useState("")
  const [again, setAgain] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setError("新密码至少 8 位，且同时包含字母和数字")
      return
    }
    if (password !== again) { setError("两次输入不一致"); return }
    if (password === oldPassword) { setError("新密码不能与旧密码相同"); return }
    setBusy(true)
    setError("")
    try {
      await changePassword(oldPassword, password)
      toast.success("密码已更新，请重新登录")
      await logout()
      navigate("/login", { replace: true })
    } catch (err) {
      setError(err.message || "修改失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base-200 px-4">
      <form className="surface-card w-full max-w-md space-y-4 p-6" onSubmit={submit}>
        <h1 className="text-lg font-semibold">修改密码</h1>
        <p className="text-sm text-base-content/60">首次登录或密码被重置后，需要先设置新密码才能继续使用。</p>
        <label className="form-control">
          <span className="label-text text-xs">当前密码</span>
          <input type="password" className="input input-bordered" value={oldPassword} onChange={(e) => setOld(e.target.value)} required />
        </label>
        <label className="form-control">
          <span className="label-text text-xs">新密码</span>
          <input type="password" className="input input-bordered" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <label className="form-control">
          <span className="label-text text-xs">确认新密码</span>
          <input type="password" className="input input-bordered" value={again} onChange={(e) => setAgain(e.target.value)} required />
        </label>
        {error && <div role="alert" className="alert alert-error py-2 text-sm">{error}</div>}
        <button className="btn btn-primary w-full" disabled={busy} type="submit">保存并重新登录</button>
      </form>
    </div>
  )
}
