import { ROLE_NAMES } from "./identity"

/** 枚举中文名的本地兜底。登录后以 GET /api/meta 为准覆盖。 */

export const FALLBACK_META = {
  stages: [
    { code: 1, name: "申请入党" },
    { code: 2, name: "确定入党积极分子" },
    { code: 3, name: "确定发展对象" },
    { code: 4, name: "接收预备党员" },
    { code: 5, name: "预备党员转正" },
  ],
  roles: Object.entries(ROLE_NAMES).map(([code, name]) => ({ code, name })),
  submission_statuses: [
    { code: "DRAFT", name: "自查中" },
    { code: "BRANCH_REVIEW", name: "支部初审" },
    { code: "CROSS_REVIEW", name: "交叉互查" },
    { code: "COLLEGE_REVIEW", name: "学院复审" },
    { code: "ORG_FILING", name: "组织部备案" },
    { code: "FILED", name: "已备案" },
    { code: "RETURNED", name: "待整改" },
  ],
  issue_categories: [
    { code: "COMPLETENESS", name: "完整性" },
    { code: "TIME", name: "时间逻辑" },
    { code: "FORMAT", name: "形式规范" },
    { code: "CONTENT", name: "内容规范" },
  ],
  severities: [
    { code: "BLOCK", name: "阻断" },
    { code: "WARN", name: "警告" },
    { code: "INFO", name: "提示" },
  ],
  review_statuses: [
    { code: "PENDING", name: "待确认" },
    { code: "CONFIRMED", name: "已确认" },
    { code: "REJECTED", name: "已驳回" },
    { code: "MODIFIED", name: "已修改" },
  ],
  recommendations: [
    { code: "SUGGEST_PASS", name: "建议通过" },
    { code: "SUGGEST_RETURN", name: "建议退回" },
    { code: "NEEDS_REVIEW", name: "需人工研判" },
  ],
  handover_statuses: [
    { code: "REQUIRED", name: "待人工审核" },
    { code: "DONE", name: "已接管" },
    { code: "NOT_REQUIRED", name: "无需接管" },
  ],
  levels: [
    { code: "BRANCH", name: "支部初审" },
    { code: "CROSS", name: "交叉互查" },
    { code: "COLLEGE", name: "学院复审" },
    { code: "ORG", name: "组织部备案" },
  ],
  material_types: [],
}

export const SEVERITY_BADGE = {
  BLOCK: "badge-error",
  WARN: "badge-warning",
  INFO: "badge-info",
}

export const STATUS_BADGE = {
  DRAFT: "badge-ghost",
  BRANCH_REVIEW: "badge-primary",
  CROSS_REVIEW: "badge-secondary",
  COLLEGE_REVIEW: "badge-accent",
  ORG_FILING: "badge-info",
  FILED: "badge-success",
  RETURNED: "badge-warning",
  ACTIVE: "badge-success",
  COMPLETED: "badge-success",
  QUEUED: "badge-ghost",
  RUNNING: "badge-info",
  SUCCEEDED: "badge-success",
  PARTIAL: "badge-warning",
  FAILED: "badge-error",
  SENT: "badge-success",
  PENDING: "badge-ghost",
  CONFIRMED: "badge-success",
  REJECTED: "badge-ghost",
  MODIFIED: "badge-info",
  OPEN: "badge-warning",
  RESOLVED: "badge-success",
  UNRESOLVED: "badge-error",
}

export const DSL_OPS = [
  { op: "age_at_least", hint: "birth, at, years" },
  { op: "before", hint: "a, b, strict, min_gap, max_gap" },
  { op: "between", hint: "x, lower, upper" },
  { op: "within", hint: "a, b, max:{value,unit}" },
  { op: "at_least", hint: "a, b, min:{value,unit}" },
  { op: "duration_min", hint: "node, min, or_hours" },
  { op: "seq_max_gap", hint: "seq, from, to, max" },
  { op: "seq_period_count", hint: "seq, from, to, period_months, min_per_period" },
  { op: "seq_in_range", hint: "seq, from, to" },
  { op: "consistent", hint: "nodes: [...] or *" },
  { op: "valid_date", hint: "nodes: *" },
  { op: "required", hint: "nodes_by_stage" },
  { op: "monotonic", hint: "nodes: [T02,T04,...]" },
  { op: "derive", hint: "name, base, offset:{value,unit}" },
]
