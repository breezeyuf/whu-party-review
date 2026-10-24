import { useState } from "react"
import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { DemoBadge, RecoBadge, StatusBadge } from "../../components/common/Badges"
import { Modal } from "../../components/common/Modal"
import { ErrorState } from "../../components/common/States"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { createArchive, listArchives } from "../../api/archives"
import { listBatches } from "../../api/batches"
import { listOrgs } from "../../api/orgs"
import { issueCountsText, stageShort } from "../../utils/format"
import { availableBranches, canManageArchive } from "../../utils/archiveWorkflow"
import { useAuth } from "../../context/AuthContext"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"

const EMPTY = {
  real_name: "", gender: "男", student_no: "", branch_id: "", batch_id: "", current_stage: "1", major: "", class_name: "",
}

export default function ArchiveListPage() {
  const meta = useMeta()
  const toast = useToast()
  const { activeRole } = useAuth()
  const canCreate = canManageArchive(activeRole)
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => listArchives(query), [JSON.stringify(query)])
  const batches = useRequest(() => listBatches({ page_size: 200 }), [])
  const orgs = useRequest(() => listOrgs({ flat: true }), [], { immediate: canCreate })
  const branches = availableBranches(orgs.data || [], activeRole)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(EMPTY)
  const [password, setPassword] = useState("")
  const [saving, setSaving] = useState(false)
  const close = () => { if (!saving) setOpen(false) }

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const save = async () => {
    if (saving) return
    if (!form.real_name.trim() || !form.student_no.trim() || !branches.some((b) => Number(b.id) === Number(form.branch_id))) {
      toast.error("请填写姓名、学号并选择支部")
      return
    }
    setSaving(true)
    try {
      const res = await createArchive({
        student: {
          real_name: form.real_name.trim(),
          gender: form.gender,
          student_no: form.student_no.trim(),
          major: form.major || undefined,
          class_name: form.class_name || undefined,
        },
        branch_id: Number(form.branch_id),
        batch_id: form.batch_id ? Number(form.batch_id) : undefined,
        current_stage: Number(form.current_stage),
      })
      setPassword(res.initial_password || "")
      toast.success("档案已创建")
      if (!res.initial_password) setOpen(false)
      req.reload().catch(() => {})
    } catch (e) {
      toast.error(e.message || "创建失败")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PageHeader title="发展档案" extra={canCreate && <button type="button" className="btn btn-primary btn-sm" onClick={() => { setForm({ ...EMPTY, branch_id: branches.length === 1 ? String(branches[0].id) : "" }); setPassword(""); setOpen(true) }}>新建档案</button>} />
      <FilterBar
        values={query}
        onChange={setQuery}
        onReset={() => setQuery({ q: "", stage_code: "", status: "", batch_id: "", submission_status: "" })}
        fields={[
          { key: "q", label: "姓名 / 学号" },
          { key: "batch_id", label: "批次", type: "select", options: (batches.data?.items || []).map((b) => ({ code: b.id, name: b.name })) },
          { key: "stage_code", label: "阶段", type: "select", metaKey: "stages" },
          { key: "status", label: "档案状态", type: "select", options: [{ code: "ACTIVE", name: "进行中" }, { code: "COMPLETED", name: "已完成" }] },
          { key: "submission_status", label: "提交状态", type: "select", metaKey: "submission_statuses" },
        ]}
      />
      {req.error && <ErrorState error={req.error} onRetry={() => req.reload().catch(() => {})} />}
      {batches.error && <div className="mb-3"><ErrorState error={batches.error} onRetry={() => batches.reload().catch(() => {})} /></div>}
      {!req.error && (
      <div className="surface-card p-2">
        <DataTable
          loading={req.loading}
          rows={req.data?.items || []}
          columns={[
            { key: "name", title: "学生", render: (r) => (
              <div>
                <Link className="link font-medium" to={`/archives/${r.id}`}>{r.real_name}</Link> <DemoBadge show={r.is_demo} />
                <div className="mono text-xs text-base-content/50">{r.student_no}</div>
              </div>
            ) },
            { key: "org", title: "组织", render: (r) => <span className="text-xs">{r.college_name}<br />{r.branch_name}</span> },
            { key: "stage", title: "阶段", render: (r) => r.stage_name || stageShort(meta, r.current_stage) },
            { key: "sub", title: "当前提交", className: "min-w-[8rem] whitespace-nowrap", render: (r) => r.submission ? (
              <Link className="link inline-flex max-w-full no-underline hover:no-underline" to={`/review/submissions/${r.submission.id}`}><StatusBadge code={r.submission.status} soft /></Link>
            ) : "—" },
            { key: "ai", title: "AI", className: "min-w-[7rem] whitespace-nowrap", render: (r) => <RecoBadge code={r.submission?.recommendation} soft /> },
            { key: "issues", title: "问题", render: (r) => <span className="text-xs">{issueCountsText(r.submission?.issue_counts)}</span> },
          ]}
        />
        <div className="px-2"><Pager page={req.data?.page} pageSize={req.data?.page_size ?? query.page_size} total={req.data?.total} onPage={setPage} onPageSize={(page_size) => setQuery({ page_size })} /></div>
      </div>
      )}
      <Modal open={open} title="新建发展档案" onClose={close} footer={
        password ? <button type="button" className="btn btn-primary btn-sm" onClick={close}>知道了</button> : (
          <>
            <button type="button" className="btn btn-ghost btn-sm" disabled={saving} onClick={close}>取消</button>
            <button type="button" className="btn btn-primary btn-sm" disabled={saving || orgs.loading || !!orgs.error || !branches.length} onClick={save}>{saving ? "创建中…" : "创建"}</button>
          </>
        )
      }>
        {password ? (
          <div className="alert">已创建学生账号，初始密码仅显示一次：<span className="mono font-medium">{password}</span></div>
        ) : (
          <div className="grid gap-2 sm:grid-cols-2">
            {orgs.error && <div className="sm:col-span-2"><ErrorState error={orgs.error} onRetry={() => orgs.reload().catch(() => {})} /></div>}
            <input className="input input-bordered input-sm" placeholder="姓名" value={form.real_name} onChange={(e) => set("real_name", e.target.value)} />
            <input className="input input-bordered input-sm" placeholder="学号" value={form.student_no} onChange={(e) => set("student_no", e.target.value)} />
            <select className="select select-bordered select-sm" value={form.gender} onChange={(e) => set("gender", e.target.value)}>
              <option>男</option><option>女</option>
            </select>
            <select aria-label="所属支部" className="select select-bordered select-sm" value={form.branch_id} disabled={saving || orgs.loading} onChange={(e) => set("branch_id", e.target.value)}>
              <option value="">{orgs.loading ? "正在加载支部…" : "选择所属支部"}</option>
              {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
            <select className="select select-bordered select-sm" value={form.batch_id} onChange={(e) => set("batch_id", e.target.value)}>
              <option value="">不指定批次</option>
              {(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
            <select className="select select-bordered select-sm" value={form.current_stage} onChange={(e) => set("current_stage", e.target.value)}>
              {(meta.stages || []).map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
            </select>
            <input className="input input-bordered input-sm" placeholder="专业" value={form.major} onChange={(e) => set("major", e.target.value)} />
            <input className="input input-bordered input-sm" placeholder="班级" value={form.class_name} onChange={(e) => set("class_name", e.target.value)} />
          </div>
        )}
      </Modal>
    </div>
  )
}
