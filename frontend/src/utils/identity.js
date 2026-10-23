const IDENTITIES = {
  STUDENT: { kind: "student", name: "申请学生", home: "/student", description: "准备材料、提交自查、处理整改和查看进度" },
  BRANCH_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  CROSS_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  COLLEGE_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  ORG_ADMIN: { kind: "admin", name: "组织管理员", home: "/admin", description: "管理组织业务、发展批次并办理备案" },
  SYS_ADMIN: { kind: "admin", name: "系统管理员", home: "/admin", description: "维护用户、组织架构和系统配置" },
}

// 角色中文名的本地兜底（constants.js 的 FALLBACK_META.roles 由此生成）。登录页、身份选择页
// 在取得 /api/meta 之前使用，放在这里可以不让登录首屏下载日期、元数据等工作台模块
export const ROLE_NAMES = {
  STUDENT: "发展学生",
  BRANCH_REVIEWER: "党支部审核员",
  CROSS_REVIEWER: "交叉互查审核员",
  COLLEGE_REVIEWER: "学院党委审核员",
  ORG_ADMIN: "学校组织部管理员",
  SYS_ADMIN: "系统管理员",
}

export function roleLabel(code) {
  if (code == null || code === "") return "—"
  return Object.hasOwn(ROLE_NAMES, code) ? ROLE_NAMES[code] : String(code)
}

export function identityFor(role) {
  return Object.hasOwn(IDENTITIES, role?.role) ? IDENTITIES[role.role] : null
}

export function roleKey(role) {
  return role ? `${role.role}@${role.org_id ?? ""}` : ""
}

export function activeOrganization(user) {
  const owned = user?.roles?.find((role) => roleKey(role) === roleKey(user?.active_role))
  return owned?.org_name || user?.org_name || "组织内部工作台"
}

export function loginDestination(user, needsIdentitySelection = false) {
  if (user?.must_change_password) return "/change-password"
  if (needsIdentitySelection || !identityFor(user?.active_role)) return "/choose-identity"
  return identityFor(user.active_role).home
}
