import { useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Loading, ErrorState } from "../../components/common/States"
import { listBatches, getCrossPairs, setCrossPairs } from "../../api/batches"
import { listOrgs } from "../../api/orgs"
import { listUsers } from "../../api/users"
import { useToast } from "../../context/ToastContext"

function flatten(nodes, acc = []) {
  (nodes || []).forEach((n) => { acc.push(n); flatten(n.children, acc) })
  return acc
}

export default function CrossReviewConfigPage() {
  const toast = useToast()
  const [batches, setBatches] = useState([])
  const [orgs, setOrgs] = useState([])
  const [batchId, setBatchId] = useState("")
  const [collegeId, setCollegeId] = useState("")
  const [pairs, setPairs] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([listBatches({ page_size: 50 }), listOrgs({ flat: true })])
      .then(([b, o]) => {
        const bl = b.items || b || []
        setBatches(bl)
        const flat = Array.isArray(o) ? (o[0]?.children ? flatten(o) : o) : (o.items || [])
        setOrgs(flat)
        if (bl[0]) setBatchId(String(bl[0].id))
        const college = flat.find((x) => x.org_type === "COLLEGE")
        if (college) setCollegeId(String(college.id))
      })
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  const colleges = orgs.filter((o) => o.org_type === "COLLEGE")
  const branches = orgs.filter((o) => o.org_type === "BRANCH" && (!collegeId || String(o.parent_id) === String(collegeId)))

  useEffect(() => {
    if (!batchId) return
    getCrossPairs(batchId, { college_id: collegeId || undefined }).then((rows) => {
      setPairs((rows || []).map((r) => ({
        target_branch_id: r.target_branch?.id,
        reviewer_branch_id: r.reviewer_branch?.id || "",
        reviewer_user_id: r.reviewer_user?.id || "",
      })))
    }).catch(() => setPairs([]))
  }, [batchId, collegeId])

  useEffect(() => {
    if (!collegeId) return
    // 互查员建在支部层级（org_id=支部），需按本学院下辖支部筛选，不能按学院 org_id 直接过滤
    listUsers({ role: "CROSS_REVIEWER", page_size: 200 }).then((d) => {
      const branchIds = new Set(
        orgs.filter((o) => o.org_type === "BRANCH" && String(o.parent_id) === String(collegeId)).map((o) => o.id),
      )
      setUsers((d.items || []).filter((u) => branchIds.has(u.org_id)))
    }).catch(() => {})
  }, [collegeId, orgs])

  const rowFor = (branchId) => pairs.find((p) => String(p.target_branch_id) === String(branchId)) || { target_branch_id: branchId, reviewer_branch_id: "", reviewer_user_id: "" }
  const update = (branchId, patch) => {
    setPairs((list) => {
      const rest = list.filter((p) => String(p.target_branch_id) !== String(branchId))
      return [...rest, { ...rowFor(branchId), ...patch, target_branch_id: Number(branchId) }]
    })
  }

  const save = async () => {
    const payload = branches.map((b) => {
      const row = rowFor(b.id)
      return {
        target_branch_id: b.id,
        reviewer_branch_id: Number(row.reviewer_branch_id),
        reviewer_user_id: row.reviewer_user_id ? Number(row.reviewer_user_id) : undefined,
      }
    }).filter((p) => p.reviewer_branch_id)
    try {
      await setCrossPairs(batchId, { college_id: Number(collegeId), pairs: payload })
      toast.success("互查配对已保存")
    } catch (e) {
      toast.error(e.message || "保存失败")
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorState error={error} />

  return (
    <div>
      <PageHeader title="交叉互查配置" extra={<button type="button" className="btn btn-primary btn-sm" onClick={save}>保存配对</button>}>
        互查支部不能是本支部。未配置的支部在初审通过后直接进入学院复审。
      </PageHeader>
      <div className="mb-4 flex flex-wrap gap-3">
        <select className="select select-bordered select-sm" value={batchId} onChange={(e) => setBatchId(e.target.value)}>
          {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
        <select className="select select-bordered select-sm" value={collegeId} onChange={(e) => setCollegeId(e.target.value)}>
          {colleges.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>
      <div className="surface-card overflow-x-auto">
        <table className="table table-sm">
          <thead><tr><th>被查支部</th><th>互查支部</th><th>指定审核人（可选）</th></tr></thead>
          <tbody>
            {branches.map((b) => {
              const row = rowFor(b.id)
              return (
                <tr key={b.id}>
                  <td>{b.name}</td>
                  <td>
                    <select className="select select-bordered select-xs" value={row.reviewer_branch_id} onChange={(e) => update(b.id, { reviewer_branch_id: e.target.value })}>
                      <option value="">不配置</option>
                      {branches.filter((x) => x.id !== b.id).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}
                    </select>
                  </td>
                  <td>
                    <select className="select select-bordered select-xs" value={row.reviewer_user_id} onChange={(e) => update(b.id, { reviewer_user_id: e.target.value })}>
                      <option value="">支部内任一互查员</option>
                      {users.map((u) => <option key={u.id} value={u.id}>{u.real_name}</option>)}
                    </select>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
