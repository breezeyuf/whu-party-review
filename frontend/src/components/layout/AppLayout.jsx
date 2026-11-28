import { useEffect, useRef, useState } from "react"
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom"
import { ChevronDown, LogOut, Menu, UserRound, X } from "lucide-react"
import { menusFor } from "../../utils/permissions"
import { isMenuActive } from "../../utils/workbench"
import { activeOrganization, identityFor } from "../../utils/identity"
import { roleName } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { useUnreadCount } from "../../hooks/useUnreadCount"

import MessageQuickActions from "./MessageQuickActions"
import ActionPopover from "../common/ActionPopover"

function NavigationGroup({ group, pathname, onNavigate }) {
  const isActive = (item) => (item.activePaths || [item.to]).some((path) => isMenuActive(pathname, path))
  const active = group.items.some(isActive)
  const [expanded, setExpanded] = useState(active || group.defaultExpanded === true)
  useEffect(() => { if (active) setExpanded(true) }, [active])
  const id = `nav-${group.group}`
  return <section className="service-nav-group">
    {group.collapsible ? <button type="button" className="service-nav-heading" aria-expanded={expanded} aria-controls={id} onClick={() => setExpanded((value) => !value)}>
      <span>{group.group}</span><ChevronDown size={15} className={expanded ? "rotate-180" : ""} />
    </button> : <p className="service-nav-label">{group.group}</p>}
    <ul id={id} hidden={group.collapsible && !expanded}>
      {group.items.map((item) => <li key={item.to}><Link to={item.to} aria-current={isActive(item) ? "page" : undefined} onClick={onNavigate} className={`service-nav-link ${isActive(item) ? "is-active" : ""}`}>{item.label}</Link></li>)}
    </ul>
  </section>
}

export default function AppLayout({ children }) {
  const { user, activeRole, logout } = useAuth()
  const toast = useToast()
  const meta = useMeta()
  const unread = useUnreadCount()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const [navOpen, setNavOpen] = useState(false)
  const menuButton = useRef(null)
  const sidebar = useRef(null)
  const main = useRef(null)
  const closeMenu = () => {
    setNavOpen(false)
    menuButton.current?.focus()
  }
  const followNavLink = () => {
    if (!navOpen) return
    setNavOpen(false)
    main.current?.focus()
  }
  const groups = menusFor(activeRole)
  const roleKey = `${activeRole?.role}@${activeRole?.org_id ?? ""}`
  const identity = identityFor(activeRole)

  useEffect(() => { setNavOpen(false) }, [pathname, roleKey])
  useEffect(() => {
    if (!navOpen) return undefined
    const nav = sidebar.current
    const entry = nav?.querySelector('a[aria-current="page"]') || nav?.querySelector("a")
    entry?.focus()
    const close = (event) => { if (event.key === "Escape" && !event.defaultPrevented) closeMenu() }
    window.addEventListener("keydown", close)
    return () => window.removeEventListener("keydown", close)
  }, [navOpen])

  return <div className="service-shell">
    <a className="skip-link" href="#main-content">跳到主要内容</a>
    <header className="service-header">
      <button ref={menuButton} type="button" className="service-menu-toggle" aria-label={navOpen ? "关闭菜单" : "打开菜单"} aria-controls="service-navigation" aria-expanded={navOpen} onClick={() => navOpen ? closeMenu() : setNavOpen(true)}>{navOpen ? <X size={21} /> : <Menu size={21} />}</button>
      <NavLink to={identity?.home || "/"} className="service-brand"><span className="service-brand-mark" aria-hidden="true">党</span><span>党员发展材料审核<span className="service-brand-subtitle">{identity?.name || "办事"}工作台</span></span></NavLink>
      <div className="service-header-actions">
        <span className="service-role-label">{roleName(meta, activeRole?.role)}</span>
        <MessageQuickActions key={`${user?.id}-${roleKey}`} unread={unread} />
        <ActionPopover key={pathname} label="个人菜单" triggerContent={<><UserRound size={18} /><span className="hidden sm:inline">{user?.real_name || user?.username}</span><ChevronDown size={13} /></>}>
          <Link to="/profile" className="btn btn-ghost btn-sm justify-start">个人中心</Link>
          <button type="button" className="btn btn-ghost btn-sm justify-start" onClick={async () => { try { await logout(); navigate("/login", { replace: true }) } catch (error) { toast.error(error.message || "退出失败，请重试") } }}><LogOut size={15} />退出登录</button>
        </ActionPopover>
      </div>
    </header>
    <div className="service-body">
      {navOpen && <button type="button" tabIndex={-1} className="service-nav-overlay" aria-label="关闭导航菜单" onPointerDown={(event) => event.preventDefault()} onClick={closeMenu} />}
      <aside ref={sidebar} id="service-navigation" className={`service-sidebar ${navOpen ? "is-open" : ""}`}
        onBlur={(event) => {
          const next = event.relatedTarget
          if (navOpen && next && next !== menuButton.current && !event.currentTarget.contains(next)) setNavOpen(false)
        }}>
        <nav aria-label="主要导航" key={roleKey}>{groups.map((group) => <NavigationGroup key={group.group} group={group} pathname={pathname} onNavigate={followNavLink} />)}</nav>
        <div className="service-sidebar-footer">{activeOrganization(user)}<br /><span>按当前身份显示可办理事项</span></div>
      </aside>
      <main ref={main} id="main-content" tabIndex={-1} className="service-main">{children}</main>
    </div>
  </div>
}
