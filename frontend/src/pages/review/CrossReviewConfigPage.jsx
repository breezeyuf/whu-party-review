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
  const [usersError, setUsersError] = useState(null)
  const [usersLoading, setUsersLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [attempt, setAttempt] = useState(0)
  const [pairsLoading, setPairsLoading] = useState(false)
  const [pairsError, setPairsError] = useState(null)
  const [pairsAttempt, setPairsAttempt] = useState(0)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([listBatches({ page_size: 200 }), listOrgs({ flat: true })])
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
  }, [attempt])

  const colleges = orgs.filter((o) => o.org_type === "COLLEGE")
  const branches = orgs.filter((o) => o.org_type === "BRANCH" && (!collegeId || String(o.parent_id) === String(collegeId)))

  useEffect(() => {
    if (!batchId || !collegeId) {
      setPairs([])
      setPairsError(null)
      setPairsLoading(false)
      return undefined
    }
    let alive = true
    setPairs([])
    setPairsError(null)
    setPairsLoading(true)
    getCrossPairs(batchId, { college_id: collegeId })
      .then((rows) => {
        if (!alive) return
        setPairs((rows || []).map((r) => ({
          target_branch_id: r.target_branch?.id,
          reviewer_branch_id: r.reviewer_branch?.id || "",
          reviewer_user_id: r.reviewer_user?.id || "",
        })))
      })
      .catch((e) => { if (alive) setPairsError(e) })
      .finally(() => { if (alive) setPairsLoading(false) })
    return () => { alive = false }
  }, [batchId, collegeId, pairsAttempt])

  useEffect(() => {
    if (!collegeId) {
      setUsers([])
      setUsersError(null)
      setUsersLoading(false)
      return undefined
    }
    let alive = true
    setUsers([])
    setUsersError(null)
    setUsersLoading(true)
    // 互查员建在支部层级（org_id=支部），需按本学院下辖支部筛选，不能按学院 org_id 直接过滤
    listUsers({ role: "CROSS_REVIEWER", page_size: 200 }).then((d) => {
      const branchIds = new Set(
        orgs.filter((o) => o.org_type === "BRANCH" && String(o.parent_id) === String(collegeId)).map((o) => String(o.id)),
      )
      if (alive) setUsers((d.items || []).filter((u) => (u.roles || []).some((grant) => grant.role === "CROSS_REVIEWER" && branchIds.has(String(grant.org_id)))))
    }).catch((e) => { if (alive) setUsersError(e) }).finally(() => { if (alive) setUsersLoading(false) })
    return () => { alive = false }
  }, [collegeId, orgs])

  const rowFor = (branchId) => pairs.find((p) => String(p.target_branch_id) === String(branchId)) || { target_branch_id: branchId, reviewer_branch_id: "", reviewer_user_id: "" }
  const update = (branchId, patch) => {
    setPairs((list) => {
      const rest = list.filter((p) => String(p.target_branch_id) !== String(branchId))
      const current = list.find((p) => String(p.target_branch_id) === String(branchId)) || { target_branch_id: branchId, reviewer_branch_id: "", reviewer_user_id: "" }
      return [...rest, { ...current, ...patch, target_branch_id: Number(branchId) }]
    })
  }

  const save = async () => {
    if (saving || loading || pairsLoading || pairsError || usersLoading || usersError || !batchId || !collegeId) return
    const configured = branches.map((b) => {
      const row = rowFor(b.id)
      return {
        target_branch_id: b.id,
        reviewer_branch_id: Number(row.reviewer_branch_id),
        reviewer_user_id: row.reviewer_user_id ? Number(row.reviewer_user_id) : undefined,
      }
    }).filter((p) => p.reviewer_branch_id)
    const assigned = new Set()
    for (const pair of configured) {
      if (!pair.reviewer_user_id) continue
      if (assigned.has(pair.reviewer_user_id)) {
        const reviewer = users.find((u) => Number(u.id) === pair.reviewer_user_id)
        toast.error(`${reviewer?.real_name || "该审核人"}已分配给其他支部，请为每个支部选择不同的审核人`)
        return
      }
      const reviewer = users.find((u) => Number(u.id) === pair.reviewer_user_id)
      if (reviewer && !(reviewer.roles || []).some((grant) => grant.role === "CROSS_REVIEWER" && String(grant.org_id) === String(pair.reviewer_branch_id))) {
        toast.error("指定审核人必须属于所选的互查支部")
        return
      }
      assigned.add(pair.reviewer_user_id)
    }
    setSaving(true)
    try {
      await setCrossPairs(batchId, { college_id: Number(collegeId), pairs: configured })
      toast.success("互查配对已保存")
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading label="互查配置" />
  if (error) return <ErrorState error={error} onRetry={() => setAttempt((value) => value + 1)} />

  return (
    <div>
      <PageHeader title="交叉互查安排" extra={<button type="button" className="btn btn-primary btn-sm" disabled={saving || loading || pairsLoading || !!pairsError || usersLoading || !!usersError || !batchId || !collegeId || !branches.length} onClick={save}>{saving ? "保存中…" : "保存配对"}</button>}>
        被查支部不能由本支部互查；每名指定审核人只能分配给一个被查支部，且审核人必须属于所选互查支部。未配置的支部在初审通过后直接进入学院复审。
      </PageHeader>
      <div className="mb-4 flex flex-wrap gap-3">
        <label className="form-control"><span className="label-text text-xs">发展批次</span><select className="select select-bordered select-sm" value={batchId} onChange={(e) => setBatchId(e.target.value)}>
          {!batches.length && <option value="">暂无批次</option>}
          {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select></label>
        <label className="form-control"><span className="label-text text-xs">学院</span><select className="select select-bordered select-sm" value={collegeId} onChange={(e) => setCollegeId(e.target.value)}>
          {!colleges.length && <option value="">暂无学院</option>}
          {colleges.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select></label>
      </div>
      {pairsError && <ErrorState title="互查配对加载失败，当前不会保存空配置" error={pairsError} onRetry={() => setPairsAttempt((value) => value + 1)} />}
      {usersError && <ErrorState title="指定审核人列表加载失败，请修复后再保存" error={usersError} onRetry={() => setAttempt((value) => value + 1)} />}
      {!batches.length || !colleges.length ? <div className="surface-card p-4 text-sm text-base-content/60">需要先建立发展批次和学院，才能配置交叉互查。</div> : <div className="surface-card overflow-x-auto">
        {pairsLoading || usersLoading ? <div className="p-4 text-sm text-base-content/60" role="status">正在加载当前学院的互查配对与审核人…</div> : null}
        <table className="table table-sm">
          <thead><tr><th>被查支部</th><th>互查支部</th><th>指定审核人（可选）</th></tr></thead>
          <tbody>
            {branches.map((b) => {
              const row = rowFor(b.id)
              return (
                <tr key={b.id}>
                  <td>{b.name}</td>
                  <td>
                    <select aria-label={`${b.name}的互查支部`} className="select select-bordered select-xs" disabled={pairsLoading || !!pairsError} value={row.reviewer_branch_id} onChange={(e) => {
                      const reviewerBranchId = e.target.value
                      const reviewer = users.find((u) => String(u.id) === String(row.reviewer_user_id))
                      const hasGrant = reviewer?.roles?.some((grant) => grant.role === "CROSS_REVIEWER" && String(grant.org_id) === reviewerBranchId)
                      update(b.id, { reviewer_branch_id: reviewerBranchId, reviewer_user_id: hasGrant ? row.reviewer_user_id : "" })
                    }}>
                      <option value="">不配置</option>
                      {branches.filter((x) => x.id !== b.id).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}
                    </select>
                  </td>
                  <td>
                    <select aria-label={`${b.name}的指定审核人`} className="select select-bordered select-xs" disabled={pairsLoading || !!pairsError || usersLoading || !!usersError || !row.reviewer_branch_id} value={row.reviewer_user_id} onChange={(e) => update(b.id, { reviewer_user_id: e.target.value })}>
                      <option value="">支部内任一互查员</option>
                      {users.filter((u) => (u.roles || []).some((grant) => grant.role === "CROSS_REVIEWER" && String(grant.org_id) === String(row.reviewer_branch_id))).map((u) => {
                        const usedElsewhere = pairs.some((p) => String(p.target_branch_id) !== String(b.id) && String(p.reviewer_user_id) === String(u.id))
                        return <option key={u.id} value={u.id} disabled={usedElsewhere}>{u.real_name}{usedElsewhere ? "（已分配）" : ""}</option>
                      })}
                    </select>
                    {usersLoading && <span className="mt-1 block text-xs text-base-content/50">正在加载审核员…</span>}
                    {!usersError && row.reviewer_branch_id && !users.some((u) => (u.roles || []).some((grant) => grant.role === "CROSS_REVIEWER" && String(grant.org_id) === String(row.reviewer_branch_id))) && <span className="mt-1 block text-xs text-base-content/50">该支部暂无可指定的互查员，或你没有查看权限；可保留“支部内任一互查员”。</span>}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>}
    </div>
  )
}
