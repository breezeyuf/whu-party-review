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
  { op: "age_at_least", label: "年龄不低于", description: "出生日期、参照日期、年数" },
  { op: "before", label: "时间先后与间隔", description: "起始节点、结束节点、严格先后、最小/最大间隔" },
  { op: "between", label: "数值范围", description: "待检查值、下限、上限" },
  { op: "within", label: "间隔不超过", description: "起止节点、最大间隔" },
  { op: "at_least", label: "间隔不少于", description: "起止节点、最小间隔" },
  { op: "duration_min", label: "培养时长下限", description: "节点、最短时长、是否按小时计算" },
  { op: "seq_max_gap", label: "序列最大间隔", description: "日期序列、起止范围、最大间隔" },
  { op: "seq_period_count", label: "分周期数量要求", description: "日期序列、起止范围、周期月数、每周期最少次数" },
  { op: "seq_in_range", label: "序列日期范围", description: "日期序列、起止范围" },
  { op: "consistent", label: "节点值一致性", description: "需要比较的节点列表，或全部节点" },
  { op: "valid_date", label: "日期有效性", description: "需要校验的节点，或全部节点" },
  { op: "required", label: "必需节点检查", description: "按发展阶段配置的必需节点" },
  { op: "monotonic", label: "节点顺序递增", description: "按先后排列的节点列表" },
  { op: "derive", label: "按基准日期推算", description: "新节点名称、基准节点、偏移量" },
]
