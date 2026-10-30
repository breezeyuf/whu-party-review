import ActorPicker from "../../components/common/ActorPicker"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { listAuditLogs } from "../../api/audit"
import { useMeta } from "../../context/MetaContext"
import { fmtDateTime, roleName } from "../../utils/format"

// 审计动作的中文说法；未收录的新动作回退显示原始代码，便于排查
const ACTION_NAME = {
  ACCESS_DENIED: "越权访问被拒",
  AI_CHECK: "AI 自查",
  ARCHIVE_CREATE: "创建档案",
  ARCHIVE_UPDATE: "更新档案",
  BATCH_CREATE: "新建批次",
  BATCH_DELETE: "删除批次",
  BATCH_IMPORT: "批量导入材料",
  BATCH_REVIEW: "批量审核通过",
  BATCH_UPDATE: "修改批次",
  CROSS_PAIRS: "配置交叉互查",
  EXPORT: "导出数据",
  FILE: "备案归档",
  HANDOVER: "材料移交",
  ISSUE_ADD: "手工添加问题",
  LOGIN: "登录",
  LOGIN_FAILED: "登录失败",
  MATERIAL_DELETE: "删除材料",
  MATERIAL_TYPE_CONFIRM: "确认材料类型",
  NODE_CORRECTION: "关键节点修正",
  ORG_CREATE: "新建组织",
  ORG_DELETE: "删除组织",
  ORG_UPDATE: "修改组织",
  PARSE_CORRECT: "解析结果修正",
  RETRY_PARSE: "重新解析材料",
  RETENTION_KEEP: "到期材料确认保留",
  REVIEW_PASS: "审核通过",
  REVIEW_RETURN: "审核退回",
  SEED_DEMO: "初始化演示数据",
  SETTINGS_UPDATE: "修改系统配置",
  SUBMIT: "提交材料",
  UPLOAD: "上传文件",
  USER_CREATE: "新建用户",
  USER_IMPORT: "批量导入用户",
  USER_RESET_PASSWORD: "重置密码",
  USER_UPDATE: "修改用户",
}

const OBJECT_NAME = {
  archive: "档案",
  batch: "批次",
  export: "导出任务",
  material: "材料",
  material_version: "材料版本",
  org: "组织",
  rule: "规则",
  settings: "系统配置",
  submission: "提交包",
  demo: "演示数据",
  user: "用户",
  "": "—",
}

export default function AuditLogsPage() {
  const meta = useMeta()
  const { query, setQuery, setPage } = usePagination()
  const { actor_label, ...requestQuery } = query
  const req = useRequest(() => listAuditLogs(requestQuery), [JSON.stringify(query)])
  return (
    <div>
      <PageHeader title="操作日志">登录、上传、审核、退回、备案、规则修改和导出都会留痕，日志不可删除。</PageHeader>
      <ActorPicker label={query.actor_label || (query.user_id ? `账号 #${query.user_id}` : query.legacy_username)} onChange={(person) => setQuery({ user_id: person?.user_id ?? "", legacy_username: person?.legacy_username ?? "", username: "", actor_label: person ? `${person.name} · ${person.username}` : "" })}/>
      <FilterBar values={query} onChange={setQuery} onReset={() => setQuery({ user_id: "", legacy_username: "", actor_label: "", username: "", action: "", object_type: "", date_from: "", date_to: "" })} fields={[
        { key: "action", label: "动作（编码）" },
        { key: "object_type", label: "对象类型" },
        { key: "date_from", label: "开始", placeholder: "YYYY-MM-DD" },
        { key: "date_to", label: "结束", placeholder: "YYYY-MM-DD" },
      ]} />
      <div className="surface-card p-2">
        <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={req.data?.items || []} empty="没有符合条件的操作记录" emptyHint="可以调整账号、动作或日期范围后再查询。" columns={[
          { key: "time", title: "时间", render: (r) => <span className="mono text-xs">{fmtDateTime(r.created_at)}</span> },
          { key: "who", title: "操作人", render: (r) => <span className="text-xs">{r.username}<br /><span className="text-base-content/50">{roleName(meta, r.role)}</span></span> },
          { key: "act", title: "动作", render: (r) => (
            <span className="text-xs" title={r.action}>{ACTION_NAME[r.action] || r.action}</span>
          ) },
          { key: "obj", title: "对象", render: (r) => <span className="text-xs">{OBJECT_NAME[r.object_type] || r.object_type || "—"} {r.object_id ? `#${r.object_id}` : ""}</span> },
          { key: "ip", title: "IP", render: (r) => <span className="mono text-xs">{r.ip}</span> },
          { key: "detail", title: "详情", render: (r) => <span className="line-clamp-2 text-xs">{typeof r.detail === "string" ? r.detail : JSON.stringify(r.detail || {})}</span> },
        ]} />
        {!req.error && <Pager page={req.data?.page ?? query.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })} />}
      </div>
    </div>
  )
}
