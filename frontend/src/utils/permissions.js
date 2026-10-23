const REVIEW_ROLES = ["BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"]

export function roleCode(active) {
  return active?.role || null
}

export function isStudent(active) {
  return roleCode(active) === "STUDENT"
}

export function isReviewer(active) {
  return REVIEW_ROLES.includes(roleCode(active))
}

export function can(active, key) {
  const r = roleCode(active)
  const map = {
    student: ["STUDENT"],
    materialRead: ["STUDENT", ...REVIEW_ROLES],
    review: REVIEW_ROLES,
    rulesRead: REVIEW_ROLES,
    rulesWrite: ["ORG_ADMIN"],
    stats: [...REVIEW_ROLES, "SYS_ADMIN"],
    export: ["ORG_ADMIN", "COLLEGE_REVIEWER"],
    batches: ["ORG_ADMIN"],
    orgs: ["SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"],
    users: ["SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"],
    settings: ["SYS_ADMIN", "ORG_ADMIN"],
    audit: ["SYS_ADMIN", "ORG_ADMIN"],
    cross: ["COLLEGE_REVIEWER", "ORG_ADMIN"],
    jobs: [...REVIEW_ROLES, "SYS_ADMIN"],
    batchUpload: ["BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"],
    notices: REVIEW_ROLES,
    archives: REVIEW_ROLES,
    seed: ["SYS_ADMIN", "ORG_ADMIN"],
  }
  return (map[key] || []).includes(r)
}

function item(to, label) {
  return { to, label }
}

export function menusFor(active) {
  const r = roleCode(active)
  if (r === "STUDENT") {
    return [{
      group: "我的",
      items: [
        item("/", "工作台"),
        item("/my/progress", "发展进度"),
        item("/my/materials", "我的材料"),
        item("/my/rectification", "整改中心"),
        item("/messages", "消息"),
      ],
    }]
  }
  const groups = []
  const adminIdentity = ["SYS_ADMIN", "ORG_ADMIN"].includes(r)
  const work = [item("/", "工作台")]
  if (!adminIdentity && can(active, "review")) work.push(item("/review/tasks", "审核待办"))
  if (!adminIdentity && can(active, "archives")) work.push(item("/archives", "发展档案"))
  work.push(item("/messages", "消息"))
  groups.push({ group: adminIdentity ? "工作台" : "日常办理", items: work })

  const tools = []
  if (adminIdentity && can(active, "review")) tools.push(item("/review/tasks", "备案待办"))
  if (adminIdentity && can(active, "archives")) tools.push(item("/archives", "发展档案"))
  if (can(active, "batchUpload")) tools.push(item("/materials/batch-upload", "批量上传"))
  if (can(active, "notices")) tools.push(item("/notices", "通知与补全"))
  if (can(active, "cross")) tools.push(item("/cross-review", "交叉互查配置"))
  if (can(active, "jobs")) tools.push(item("/tasks/jobs", "任务进度"))
  if (tools.length) groups.push({ group: "更多业务", collapsible: true, items: tools })

  if (can(active, "rulesRead")) {
    groups.push({
      group: "规则库",
      collapsible: true,
      items: [
        item("/rules/checklists", "材料清单"),
        item("/rules/material-types", "材料类型"),
        item("/rules/time-rules", "时间规则"),
        item("/rules/check-rules", "形式与内容规则"),
        item("/rules/terms", "术语库"),
        item("/rules/sensitive", "敏感表述"),
        item("/rules/suggestions", "修改建议模板"),
        item("/rules/versions", "规则版本"),
      ],
    })
  }
  if (can(active, "stats")) {
    const stats = [
      item("/stats/overview", "审核统计"),
      item("/stats/ai-quality", "AI 效能"),
    ]
    if (can(active, "export")) stats.push(item("/stats/export", "数据导出"))
    groups.push({ group: "统计", collapsible: true, items: stats })
  }
  const admin = []
  if (can(active, "batches")) admin.push(item("/admin/batches", "发展批次"))
  if (can(active, "orgs")) admin.push(item("/admin/orgs", "组织架构"))
  if (can(active, "users")) admin.push(item("/admin/users", "用户管理"))
  if (can(active, "settings")) admin.push(item("/admin/settings", "系统配置"))
  if (can(active, "audit")) admin.push(item("/admin/audit-logs", "审计日志"))
  if (admin.length) groups.push({ group: "管理", collapsible: !adminIdentity, items: admin })
  return groups
}
