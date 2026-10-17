import { NavLink, useNavigate } from "react-router-dom"
import { Bell, LogOut, UserRound } from "lucide-react"
import { menusFor } from "../../utils/permissions"
import { roleName as roleLabel } from "../../utils/format"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { useUnreadCount } from "../../hooks/useUnreadCount"

export default function AppLayout({ children }) {
  const { user, activeRole, roles, switchRole, logout } = useAuth()
  const meta = useMeta()
  const unread = useUnreadCount()
  const navigate = useNavigate()
  const groups = menusFor(activeRole)

  const onLogout = async () => {
    await logout()
    navigate("/login", { replace: true })
  }

  const onSwitch = async (e) => {
    const [role, org] = e.target.value.split("@")
    const found = roles.find((r) => r.role === role && String(r.org_id ?? "") === String(org ?? ""))
    if (found) await switchRole(found)
  }

  return (
    <div className="drawer lg:drawer-open min-h-screen bg-base-200">
      <input id="nav-drawer" type="checkbox" className="drawer-toggle" />
      <div className="drawer-content flex min-h-screen flex-col">
        <header className="navbar navbar-glass sticky top-0 z-30 border-b border-base-300 px-3 lg:px-6">
          <div className="flex-none lg:hidden">
            <label htmlFor="nav-drawer" aria-label="打开菜单" className="btn btn-square btn-ghost btn-sm">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </label>
          </div>
          <div className="flex-1 px-2">
            <span className="text-sm font-semibold tracking-tight">党员发展材料智能审核</span>
          </div>
          <div className="flex items-center gap-2">
            {roles.length > 1 && (
              <select
                className="select select-bordered select-sm w-44"
                aria-label="切换当前角色"
                value={activeRole ? `${activeRole.role}@${activeRole.org_id ?? ""}` : ""}
                onChange={onSwitch}
              >
                {roles.map((r) => (
                  <option key={`${r.role}@${r.org_id}`} value={`${r.role}@${r.org_id ?? ""}`}>
                    {roleLabel(meta, r.role)}
                  </option>
                ))}
              </select>
            )}
            {roles.length <= 1 && activeRole && (
              <span className="badge badge-ghost badge-sm">{roleLabel(meta, activeRole.role)}</span>
            )}
            <button type="button" className="btn btn-ghost btn-sm btn-circle" aria-label="消息" onClick={() => navigate("/messages")}>
              <div className="indicator">
                <Bell size={16} />
                {unread > 0 && <span className="indicator-item badge badge-primary badge-xs">{unread > 99 ? "99+" : unread}</span>}
              </div>
            </button>
            <div className="dropdown dropdown-end">
              <button type="button" tabIndex={0} className="btn btn-ghost btn-sm gap-2">
                <UserRound size={16} />
                <span className="hidden max-w-28 truncate sm:inline">{user?.real_name || user?.username}</span>
              </button>
              <ul tabIndex={0} className="dropdown-content menu z-40 mt-2 w-44 rounded-lg border border-base-300 bg-base-100 p-1 shadow-sm">
                <li><button type="button" onClick={() => navigate("/profile")}>个人中心</button></li>
                <li><button type="button" onClick={onLogout}><LogOut size={14} /> 退出登录</button></li>
              </ul>
            </div>
          </div>
        </header>
        <main className="container mx-auto w-full max-w-7xl flex-1 px-4 py-6 lg:px-8">{children}</main>
      </div>
      <div className="drawer-side z-40">
        <label htmlFor="nav-drawer" aria-label="关闭菜单" className="drawer-overlay" />
        <aside className="flex min-h-full w-60 flex-col border-r border-base-300 bg-base-100">
          <div className="border-b border-base-300 px-4 py-4">
            <div className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-content shadow-sm">党</span>
              <div>
                <div className="text-xs tracking-wide text-base-content/50">工作台</div>
                <div className="mt-0.5 text-sm font-semibold leading-4">材料审核</div>
              </div>
            </div>
          </div>
          <nav className="menu menu-sm flex-1 gap-1 p-2">
            {groups.map((g) => (
              <li key={g.group}>
                <div className="menu-title px-2 pt-3 text-[11px] uppercase tracking-wider text-base-content/40">{g.group}</div>
                <ul>
                  {g.items.map((it) => (
                    <li key={it.to}>
                      <NavLink
                        to={it.to}
                        end={it.to === "/"}
                        className={({ isActive }) => isActive ? "active font-medium" : ""}
                      >
                        {it.label}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </nav>
          <div className="border-t border-base-300 px-4 py-3 text-[11px] text-base-content/40">
            {user?.org_name || "—"} · {activeRole ? roleLabel(meta, activeRole.role) : ""}
          </div>
        </aside>
      </div>
    </div>
  )
}
