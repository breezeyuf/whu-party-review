import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import DataTable, { Pager } from "../../components/common/DataTable"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { dryRun, ruleVersion, ruleVersions } from "../../api/rules"
import { fmtDateTime } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { can } from "../../utils/permissions"

const CHANGE_KIND = {
  checklists: "材料清单",
  "material-types": "材料类型",
  "time-nodes": "时间节点",
  "time-rules": "时间规则",
  "check-rules": "内容规则",
  terms: "术语库",
  "sensitive-phrases": "敏感表述",
  "suggestion-templates": "修改建议模板",
  "prompt-templates": "提示词模板",
  init: "系统初始化",
}
const CHANGE_ACTION = { INIT: "初始化", CREATE: "新增", UPDATE: "修改", DELETE: "删除", IMPORT: "导入" }

// 差异表里的常见字段名
const FIELD_NAME = {
  name: "名称",
  code: "编码",
  stage_codes: "适用阶段",
  title_keywords: "识别关键词",
  exclude_keywords: "排除关键词",
  element_template: "内容要素模板",
  format_requirements: "形式要素",
  description: "说明",
  is_active: "是否启用",
  severity: "级别",
  engine: "引擎",
  condition: "条件",
  message: "提示语",
  suggestion: "修改建议",
  quantity_mode: "份数方式",
  fixed_count: "固定份数",
  period_months: "周期（月）",
  period_start_node: "周期起点",
  period_end_node: "周期终点",
  is_required: "是否必需",
  requirement_text: "提交要求",
  sort_order: "排序",
  standard_text: "标准表述",
  wrong_variants: "错误写法",
  sequence_items: "顺序条目",
  term_type: "术语类型",
  phrase: "表述",
  match_type: "匹配方式",
  risk_level: "风险级别",
  risk_note: "风险说明",
  template: "模板",
  variables: "变量",
  rule_code: "适用规则",
  expr: "表达式",
  value_kind: "取值类型",
  stage_code: "阶段",
}

export default function RuleVersionsPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const writable = can(activeRole, "rulesWrite")
  const { query, setPage } = usePagination()
  const req = useRequest(() => ruleVersions(query), [JSON.stringify(query)])
  const [left, setLeft] = useState("")
  const [right, setRight] = useState("")
  const [diff, setDiff] = useState(null)
  const [trialIds, setTrialIds] = useState("")
  const [trial, setTrial] = useState(null)

  const compare = async () => {
    if (!left || !right) { toast.error("请先分别选择版本 A 和版本 B"); return }
    if (left.id === right.id) { toast.error("请选择两个不同的规则版本再对比"); return }
    try {
      setDiff(await ruleVersion(left.id, { diff_with: right.id }))
    } catch (e) {
      toast.error(e.message || "版本对比失败")
    }
  }

  const run = async () => {
    const submission_ids = trialIds.split(/[,，\s]+/).map(Number).filter(Boolean).slice(0, 20)
    if (!submission_ids.length) { toast.error("填写最多 20 个提交包 ID"); return }
    setTrial(await dryRun({ submission_ids, overrides: {} }))
    toast.success("试运行完成（不写库）")
  }

  return (
    <div>
      <PageHeader title="规则版本" />
      <div className="alert mb-3 items-start border border-base-300 bg-base-100 text-sm">
        <div>
          <p className="font-medium">这里记录“审核规则什么时候、改了什么”。</p>
          <p className="mt-1 text-xs text-base-content/65">每次调整材料清单、时间要求或内容校验规则，都会生成一个版本。选两个版本可查看字段变化；“规则试运行”仅对已有提交包预演当前规则，不会修改审核报告或正式数据。</p>
        </div>
      </div>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} rows={req.data?.items || []} columns={[
          { key: "no", title: "版本", render: (r) => <span className="mono">v{r.version_no}</span> },
          { key: "kind", title: "变更", render: (r) => <span className="text-xs">{CHANGE_KIND[r.change_kind] || r.change_kind || "—"}{r.change_kind !== "init" && CHANGE_ACTION[r.change_action] ? ` · ${CHANGE_ACTION[r.change_action]}` : ""}</span> },
          { key: "sum", title: "摘要", render: (r) => <span className="text-xs">{r.change_summary}</span> },
          { key: "who", title: "操作人", render: (r) => <span className="text-xs">{r.created_by_name}<br />{fmtDateTime(r.created_at)}</span> },
          { key: "rep", title: "关联报告", render: (r) => r.report_count ?? 0 },
          { key: "pick", title: "对比", render: (r) => (
            <span className="flex gap-1">
              <button type="button" className={`btn btn-xs ${left.id === r.id ? "btn-primary" : "btn-ghost"}`} aria-label={`选择 v${r.version_no} 为版本 A`} onClick={() => setLeft({ id: r.id, version_no: r.version_no })}>选为 A</button>
              <button type="button" className={`btn btn-xs ${right.id === r.id ? "btn-primary" : "btn-ghost"}`} aria-label={`选择 v${r.version_no} 为版本 B`} onClick={() => setRight({ id: r.id, version_no: r.version_no })}>选为 B</button>
            </span>
          ) },
        ]} />
        <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />
      </div>
      <div className="mt-4 flex flex-wrap items-end gap-2">
        <span className="text-xs">版本 A：{left ? `v${left.version_no}` : "未选择"}　版本 B：{right ? `v${right.version_no}` : "未选择"}</span>
        <button type="button" className="btn btn-outline btn-sm" onClick={compare}>对比两个版本</button>
      </div>
      {diff?.changes && (
        <div className="surface-card mt-3 overflow-x-auto">
          <table className="table table-xs">
            <thead><tr><th>对象</th><th>编码</th><th>字段</th><th>旧</th><th>新</th></tr></thead>
            <tbody>
              {diff.changes.map((c, i) => (
                <tr key={i}>
                  <td>{CHANGE_KIND[c.kind] || c.kind}</td><td className="mono text-xs">{c.code}</td><td className="text-xs">{FIELD_NAME[c.field] || c.field}</td>
                  <td className="max-w-48 text-xs">{JSON.stringify(c.old)}</td>
                  <td className="max-w-48 text-xs">{JSON.stringify(c.new)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!diff.changes.length && <p className="p-3 text-sm text-base-content/50">两个版本没有差异。</p>}
        </div>
      )}
      {writable && (
        <section className="surface-card mt-4 p-4">
          <h2 className="text-sm font-medium">规则试运行</h2>
          <p className="mt-1 text-xs text-base-content/55">提交包 ID 可在审核工作区或提交详情地址中查看。输入最多 20 个 ID 后，系统会用当前规则预演并显示新增/消失的问题；不会保存报告，也不会改动正式审核结论。</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <input className="input input-bordered input-sm w-72" placeholder="提交包 ID，逗号分隔" value={trialIds} onChange={(e) => setTrialIds(e.target.value)} />
            <button type="button" className="btn btn-outline btn-sm" onClick={run}>试运行</button>
          </div>
          {trial && (
            <ul className="mt-3 space-y-2 text-xs">
              {(trial.results || []).map((r) => (
                <li key={r.submission_id} className="surface-card p-2">
                  提交包 {r.submission_id} · 新增 {(r.added || []).length} · 消失 {(r.removed || []).length}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  )
}
