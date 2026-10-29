import { useRequest } from "../../hooks/useRequest"
import { listOrgs } from "../../api/orgs"
import { listBatches } from "../../api/batches"
import { useAuth } from "../../context/AuthContext"
import FilterBar from "../common/FilterBar"
import { ErrorState } from "../common/States"

export default function StatsFilters({ value, onChange, exportMode = false }) {
  const { activeRole } = useAuth()
  const options = useRequest(async () => {
    const [orgs, first] = await Promise.all([listOrgs({ flat: true }), listBatches({ page: 1, page_size: 100 })])
    const batches = [...(first.items || [])]
    for (let page = 2; batches.length < (first.total || 0); page++) {
      const next = await listBatches({ page, page_size: 100 })
      if (!next.items?.length) throw new Error("批次列表不完整，请重试")
      batches.push(...next.items)
    }
    return { orgs, batches }
  }, [])
  const orgs = options.data?.orgs || []
  const allStats = ["ORG_ADMIN", "SYS_ADMIN"].includes(activeRole?.role)
  const colleges = orgs.filter((o) => o.org_type === "COLLEGE" && (allStats || Number(o.id) === Number(activeRole?.org_id)))
  const branches = orgs.filter((o) => o.org_type === "BRANCH" && (!value.college_id || Number(o.parent_id) === Number(value.college_id)) && (allStats || Number(o.parent_id) === Number(activeRole?.org_id) || Number(o.id) === Number(activeRole?.org_id)))
  return <div>
    {options.error && <ErrorState error={options.error} onRetry={options.reload} />}
    <FilterBar values={value} onChange={(patch) => onChange({ ...value, ...patch, ...("college_id" in patch ? { branch_id: "" } : {}) })} onReset={() => onChange({})} fields={[
      { key: "batch_id", label: "批次", type: "select", options: (options.data?.batches || []).map((o) => ({ code: o.id, name: o.name })) },
      { key: "college_id", label: "学院", type: "select", options: colleges.map((o) => ({ code: o.id, name: o.name })) },
      ...(!exportMode ? [{ key: "branch_id", label: "支部", type: "select", options: branches.map((o) => ({ code: o.id, name: o.name })) }] : []),
      { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
      { key: "date_from", label: "开始日期", placeholder: "YYYY-MM-DD" },
      { key: "date_to", label: "结束日期", placeholder: "YYYY-MM-DD" },
    ]} />
  </div>
}
