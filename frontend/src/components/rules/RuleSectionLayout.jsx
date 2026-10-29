import { Link, Outlet, useLocation } from "react-router-dom"

const SECTIONS = [
  {
    title: "材料标准",
    paths: ["/rules/checklists", "/rules/material-types"],
    tabs: [
      ["/rules/checklists", "材料清单"],
      ["/rules/material-types", "材料类型与模板"],
    ],
  },
  {
    title: "审核规则",
    paths: ["/rules/time-rules", "/rules/check-rules", "/rules/terms", "/rules/sensitive"],
    tabs: [
      ["/rules/time-rules", "时间规则"],
      ["/rules/check-rules", "形式与内容规则"],
      ["/rules/terms", "规范术语"],
      ["/rules/sensitive", "敏感表述库"],
    ],
  },
  {
    title: "规则治理",
    paths: ["/rules/suggestions", "/rules/versions"],
    tabs: [
      ["/rules/suggestions", "整改建议模板"],
      ["/rules/versions", "规则版本与发布"],
    ],
  },
]

export default function RuleSectionLayout() {
  const { pathname } = useLocation()
  const section = SECTIONS.find((item) => item.paths.includes(pathname))
  if (!section) return <Outlet />

  return (
    <div className="rule-section-layout">
      <nav className="mb-4" aria-label={section.title}>
        <h2 className="mb-2 text-2xl font-semibold text-base-content">{section.title}</h2>
        <div role="tablist" className="tabs tabs-bordered w-full overflow-x-auto" aria-label={`${section.title}功能`}>
          {section.tabs.map(([to, label]) => {
            const active = pathname === to
            return <Link key={to} role="tab" aria-selected={active} aria-current={active ? "page" : undefined} className={`tab whitespace-nowrap ${active ? "tab-active" : ""}`} to={to}>{label}</Link>
          })}
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
