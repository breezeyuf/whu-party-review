import { useState } from "react"
import { Navigate, useNavigate } from "react-router-dom"
import { ArrowRight, GraduationCap, ShieldCheck, ClipboardCheck } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { identityFor, loginDestination, roleKey } from "../utils/identity"
import { roleName } from "../utils/format"
import { FALLBACK_META } from "../utils/constants"

const icons = { student: GraduationCap, admin: ShieldCheck, reviewer: ClipboardCheck }

export default function ChooseIdentityPage() {
  const { user, roles, needsIdentitySelection, switchRole, logout } = useAuth()
  const navigate = useNavigate()
  const [busy, setBusy] = useState("")
  const [error, setError] = useState("")
  if (!needsIdentitySelection && identityFor(user?.active_role)) return <Navigate to={loginDestination(user)} replace />
  const choices = roles.filter((role) => identityFor(role))
  const choose = async (role) => {
    if (busy) return
    setBusy(roleKey(role)); setError("")
    try { const me = await switchRole(role); navigate(loginDestination(me), { replace: true }) }
    catch (err) { setError(err.message || "无法进入此身份，请重试") }
    finally { setBusy("") }
  }
  return <main className="identity-screen"><div className="identity-panel">
    <p className="section-eyebrow">党员发展材料审核</p>
    <h1>选择本次办理身份</h1>
    <p className="identity-intro">{user?.real_name || user?.username}，请选择一个身份进入专属工作台。</p>
    {error && <div className="alert alert-error mb-4" role="alert">{error}</div>}
    <div className="identity-choices">{choices.map((role) => {
      const identity = identityFor(role)
      const Icon = icons[identity.kind]
      return <button key={roleKey(role)} type="button" className="identity-choice" disabled={!!busy} onClick={() => choose(role)}>
        <Icon size={25} aria-hidden="true" /><span><strong>{roleName(FALLBACK_META, role.role)}</strong><small>{role.org_name || user?.org_name || "所属组织"}{role.org_name ? "" : role.org_id != null ? ` · 组织 ${role.org_id}` : ""}</small><span>{identity.description}</span></span>{busy === roleKey(role) ? <span className="loading loading-spinner loading-sm" /> : <ArrowRight size={19} aria-hidden="true" />}
      </button>
    })}</div>
    {!choices.length && <p className="alert">该账号暂无可用身份，请联系管理员开通权限。</p>}
    <button type="button" className="quiet-link mt-6" disabled={!!busy} onClick={async () => { await logout(); navigate("/login", { replace: true }) }}>退出登录</button>
  </div></main>
}
