const IDENTITIES = {
  STUDENT: { kind: "student", name: "申请学生", home: "/student", description: "准备材料、提交自查、处理整改和查看进度" },
  BRANCH_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  CROSS_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  COLLEGE_REVIEWER: { kind: "reviewer", name: "审核员", home: "/review", description: "核对材料、处理审核待办和查看发展档案" },
  ORG_ADMIN: { kind: "admin", name: "组织管理员", home: "/admin", description: "管理组织业务、发展批次并办理备案" },
  SYS_ADMIN: { kind: "admin", name: "系统管理员", home: "/admin", description: "维护用户、组织架构和系统配置" },
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
