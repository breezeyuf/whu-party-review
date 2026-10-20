import { useEffect, useRef, useState } from "react"
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom"
import { Bell, ChevronDown, LogOut, Menu, UserRound, X } from "lucide-react"
import { menusFor } from "../../utils/permissions"
import { isMenuActive } from "../../utils/workbench"
import { activeOrganization, identityFor } from "../../utils/identity"
import { roleName } from "../../utils/format"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { useUnreadCount } from "../../hooks/useUnreadCount"

function NavigationGroup({ group, pathname, onNavigate }) {
  const active = group.items.some((item) => isMenuActive(pathname, item.to))
  const [expanded, setExpanded] = useState(active)
  useEffect(() => { if (active) setExpanded(true) }, [active])
  const id = `nav-${group.group}`
  return <section className="service-nav-group">
    {group.collapsible ? <button type="button" className="service-nav-heading" aria-expanded={expanded} aria-controls={id} onClick={() => setExpanded((value) => !value)}>
      <span>{group.group}</span><ChevronDown size={15} className={expanded ? "rotate-180" : ""} />
    </button> : <p className="service-nav-label">{group.group}</p>}
    <ul id={id} hidden={group.collapsible && !expanded}>
      {group.items.map((item) => <li key={item.to}><Link to={item.to} aria-current={isMenuActive(pathname, item.to) ? "page" : undefined} onClick={onNavigate} className={`service-nav-link ${isMenuActive(pathname, item.to) ? "is-active" : ""}`}>{item.label}</Link></li>)}
    </ul>
  </section>
}

export default function AppLayout({ children }) {
  const { user, activeRole, logout } = useAuth()
  const meta = useMeta()
  const unread = useUnreadCount()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const [navOpen, setNavOpen] = useState(false)
  const menuButton = useRef(null)
  const groups = menusFor(activeRole)
  const roleKey = `${activeRole?.role}@${activeRole?.org_id ?? ""}`
  const identity = identityFor(activeRole)

  useEffect(() => { setNavOpen(false) }, [pathname, roleKey])
  useEffect(() => {
    if (!navOpen) return undefined
    const close = (event) => { if (event.key === "Escape") { setNavOpen(false); menuButton.current?.focus() } }
    window.addEventListener("keydown", close)
    return () => window.removeEventListener("keydown", close)
  }, [navOpen])

  return <div className="service-shell">
    <a className="skip-link" href="#main-content">跳到主要内容</a>
    <header className="service-header">
      <button ref={menuButton} type="button" className="service-menu-toggle" aria-label={navOpen ? "关闭菜单" : "打开菜单"} aria-controls="service-navigation" aria-expanded={navOpen} onClick={() => setNavOpen((value) => !value)}>{navOpen ? <X size={21} /> : <Menu size={21} />}</button>
      <NavLink to={identity?.home || "/"} className="service-brand"><span className="service-brand-mark" aria-hidden="true">党</span><span>党员发展材料审核<span className="service-brand-subtitle">{identity?.name || "办事"}工作台</span></span></NavLink>
      <div className="service-header-actions">
        <span className="service-role-label">{roleName(meta, activeRole?.role)}</span>
        <button type="button" className="btn btn-ghost btn-sm" aria-label={`消息${unread ? `，${unread} 条未读` : ""}`} onClick={() => navigate("/messages")}><Bell size={18} /><span className="hidden sm:inline">消息</span>{unread > 0 && <span className="badge badge-primary badge-xs">{unread > 99 ? "99+" : unread}</span>}</button>
        <details className="service-account"><summary aria-label="个人菜单"><UserRound size={18} /><span className="hidden sm:inline">{user?.real_name || user?.username}</span><ChevronDown size={13} /></summary><div className="service-account-menu"><button type="button" onClick={() => navigate("/profile")}>个人资料</button><button type="button" onClick={async () => { await logout(); navigate("/login", { replace: true }) }}><LogOut size={15} />退出登录</button></div></details>
      </div>
    </header>
    <div className="service-body">
      {navOpen && <button type="button" className="service-nav-overlay" aria-label="关闭导航菜单" onClick={() => setNavOpen(false)} />}
      <aside id="service-navigation" className={`service-sidebar ${navOpen ? "is-open" : ""}`}>
        <nav aria-label="主要导航" key={roleKey}>{groups.map((group) => <NavigationGroup key={group.group} group={group} pathname={pathname} onNavigate={() => setNavOpen(false)} />)}</nav>
        <div className="service-sidebar-footer">{activeOrganization(user)}<br /><span>按当前身份显示可办理事项</span></div>
      </aside>
      <main id="main-content" tabIndex={-1} className="service-main">{children}</main>
    </div>
  </div>
}
