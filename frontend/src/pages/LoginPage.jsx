import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { ShieldCheck, FileSearch, GitBranch, BellRing } from "lucide-react"
import { demoAccounts } from "../api/auth"
import { useAuth } from "../context/AuthContext"
import { loginDestination, roleLabel } from "../utils/identity"
import { whenIdle } from "../utils/lazyLoad"
import { preloadShell } from "../components/layout/lazyShell"

const FEATURES = [
  { icon: FileSearch, title: "AI 材料自查", desc: "清单核对、时间节点抽取与敏感表述检查" },
  { icon: GitBranch, title: "多级审核流转", desc: "自查、初审、互查、复审、备案全程留痕" },
  { icon: ShieldCheck, title: "关键阶段人工接管", desc: "低置信度与冲突结论强制人工研判" },
  { icon: BellRing, title: "整改闭环提醒", desc: "问题逐项回复、到期预警与消息通知" },
]

export default function LoginPage() {
  const { login, user, ready, needsIdentitySelection } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    if (ready && user) navigate(loginDestination(user, needsIdentitySelection), { replace: true })
  }, [user, ready, needsIdentitySelection, navigate])

  useEffect(() => {
    demoAccounts().then((list) => setAccounts(Array.isArray(list) ? list : [])).catch(() => {})
  }, [])

  // 空闲时预取登录后的外壳，登录成功进入工作台时不再等待下载
  useEffect(() => whenIdle(preloadShell), [])

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError("")
    try {
      const data = await login(username.trim(), password)
      navigate(loginDestination(data.me, data.needsIdentitySelection), { replace: true })
    } catch (err) {
      setError(err?.message || err?.response?.data?.message || "登录失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-base-200">
      {/* 品牌区 */}
      <aside className="brand-panel hidden w-[46%] flex-col justify-center gap-12 p-10 lg:flex lg:sticky lg:top-0 lg:h-screen xl:px-14">
        <div className="flex items-center gap-3">
          <span className="brand-dot flex h-9 w-9 items-center justify-center rounded-lg text-lg font-bold">党</span>
          <span className="text-sm font-medium tracking-wide opacity-90">党员发展材料智能审核工作台</span>
        </div>
        <div>
          <h1 className="text-3xl font-semibold leading-snug tracking-tight xl:text-4xl">
            材料审核，<br />一次提交，全程可溯。
          </h1>
          <p className="mt-4 max-w-md text-sm leading-6 opacity-80">
            覆盖申请、培养、接收、转正各阶段材料的自查与多级审核，AI 辅助核对与人工研判结合。
          </p>
          <ul className="mt-8 space-y-4">
            {FEATURES.map((f) => (
              <li key={f.title} className="flex items-start gap-3">
                <span className="brand-dot mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-lg">
                  <f.icon size={16} />
                </span>
                <span>
                  <span className="block text-sm font-medium">{f.title}</span>
                  <span className="block text-xs opacity-70">{f.desc}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="text-xs opacity-60">仅限组织内部账号使用</div>
      </aside>

      {/* 表单区 */}
      <div className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center lg:hidden">
            <h1 className="text-2xl font-semibold tracking-tight">党员发展材料智能审核</h1>
            <p className="mt-2 text-sm text-base-content/60">申请、培养、接收、转正材料的自查与多级审核</p>
          </div>
          <div className="mb-6 hidden lg:block">
            <div className="text-xs tracking-[0.2em] text-base-content/40">欢迎回来</div>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">登录工作台</h2>
          </div>
          <form className="surface-card space-y-4 p-6" onSubmit={submit}>
            <label className="form-control">
              <span className="label-text mb-1 text-xs">工号 / 学号</span>
              <input className="input input-bordered" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </label>
            <label className="form-control">
              <span className="label-text mb-1 text-xs">密码</span>
              <input type="password" className="input input-bordered" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </label>
            {error && <div role="alert" className="alert alert-error py-2 text-sm">{error}</div>}
            <button type="submit" className="btn btn-primary w-full" disabled={busy}>
              {busy && <span className="loading loading-spinner loading-xs" />}
              {busy ? "正在登录…" : "登录"}
            </button>
            <p className="text-center text-xs text-base-content/60">登录后按账号身份进入学生、审核或管理工作台。</p>
            <p className="text-center text-xs text-base-content/45">账号由组织开通，不开放自助注册。连续输错 5 次将锁定 15 分钟。</p>
          </form>
          {accounts.length > 0 && (
            <details className="mt-4 surface-card p-4">
              <summary className="cursor-pointer text-xs font-medium text-base-content/60">查看演示账号</summary>
              <ul className="mt-2 max-h-56 space-y-1 overflow-y-auto pr-1">
                {accounts.map((a) => (
                  <li key={a.username}>
                    <button
                      type="button"
                      className="btn btn-ghost btn-xs w-full justify-between"
                      onClick={() => { setUsername(a.username); setPassword(a.password_hint || "") }}
                    >
                      <span>{a.real_name} · {a.username}</span>
                      <span className="text-base-content/40">{Array.from(new Set((a.roles || []).map((r) => roleLabel(r.role || r)))).join(" / ")}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </div>
    </div>
  )
}
