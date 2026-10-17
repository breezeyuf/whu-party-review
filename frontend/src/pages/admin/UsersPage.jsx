import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { Modal } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { createUser, importTemplate, importUsers, listUsers, resetPassword, updateUser } from "../../api/users"
import { saveBlob } from "../../api/client"
import { listBatches } from "../../api/batches"
import { listOrgs } from "../../api/orgs"
import { roleName, fmtDateTime } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"

const ROLES = ["STUDENT", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN", "SYS_ADMIN"]

export default function UsersPage() {
  const meta = useMeta()
  const toast = useToast()
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => listUsers(query), [JSON.stringify(query)])
  const batches = useRequest(() => listBatches({ page_size: 20 }), [])
  const orgs = useRequest(() => listOrgs({ flat: true }), [])
  const [edit, setEdit] = useState(null)
  const [secret, setSecret] = useState("")
  const [importResult, setImportResult] = useState(null)
  const [batchId, setBatchId] = useState("")

  const save = async () => {
    if (!edit.real_name || !edit.org_id || (!edit.id && !edit.username)) {
      toast.error("请填写用户名、姓名并选择组织")
      return
    }
    const roles = String(edit.role || "").split(",").map((s) => s.trim()).filter(Boolean).map((role) => ({ role, org_id: Number(edit.org_id) }))
    try {
      if (edit.id) {
        await updateUser(edit.id, { real_name: edit.real_name, org_id: Number(edit.org_id), roles, is_active: edit.is_active !== false })
        toast.success("已更新")
        setEdit(null)
      } else {
        const res = await createUser({ username: edit.username, real_name: edit.real_name, org_id: Number(edit.org_id), roles })
        setSecret(res.initial_password || "")
        toast.success("用户已创建")
      }
      req.reload()
    } catch (e) {
      toast.error(e.message || "保存失败")
    }
  }

  const reset = async (row) => {
    try {
      const res = await resetPassword(row.id)
      setSecret(res.initial_password || "")
      setEdit(null)
      toast.success("密码已重置")
    } catch (e) {
      toast.error(e.message || "重置失败")
    }
  }

  const doImport = async (file, dryRun) => {
    try {
      const res = await importUsers(file, { dryRun, batchId: batchId || undefined })
      setImportResult(res)
      if (!dryRun) req.reload()
    } catch (e) {
      // 导入失败（含整体回滚）时展示错误明细
      const errs = e.data?.errors || [{ message: e.message || "导入失败" }]
      setImportResult({ total: 0, valid: 0, created_users: 0, created_archives: 0, errors: errs })
      toast.error(e.message || "导入失败")
    }
  }

  return (
    <div>
      <PageHeader title="用户管理" extra={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={async () => saveBlob(await importTemplate())}>下载导入模板</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => { setSecret(""); setEdit({ username: "", real_name: "", org_id: "", role: "STUDENT", is_active: true }) }}>新增用户</button>
        </>
      } />
      <FilterBar values={query} onChange={setQuery} onReset={() => setQuery({ q: "", role: "", org_id: "", is_active: "" })} fields={[
        { key: "q", label: "姓名 / 账号" },
        { key: "role", label: "角色", type: "select", metaKey: "roles" },
        { key: "org_id", label: "组织 ID" },
        { key: "is_active", label: "状态", type: "select", options: [{ code: "true", name: "启用" }, { code: "false", name: "停用" }] },
      ]} />
      {req.error && (
        <div className="alert alert-error mb-4 flex items-center justify-between gap-3 text-sm" role="alert">
          <span>{req.error.message || "用户列表加载失败"}</span>
          <button type="button" className="btn btn-error btn-outline btn-xs" onClick={() => req.reload()}>
            重新加载
          </button>
        </div>
      )}
      <div className="surface-card mb-4 p-3 text-sm">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="text-xs text-base-content/60">Excel 导入</span>
          <select className="select select-bordered select-xs" value={batchId} onChange={(e) => setBatchId(e.target.value)}>
            <option value="">不建档</option>
            {(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
          <label className="btn btn-outline btn-xs">预校验<input type="file" accept=".xlsx" className="hidden" onChange={(e) => e.target.files?.[0] && doImport(e.target.files[0], true)} /></label>
          <label className="btn btn-primary btn-xs">正式导入<input type="file" accept=".xlsx" className="hidden" onChange={(e) => e.target.files?.[0] && doImport(e.target.files[0], false)} /></label>
        </div>
        {importResult && (
          <div className="text-xs">
            共 {importResult.total} 行，有效 {importResult.valid}，新建用户 {importResult.created_users ?? 0}，档案 {importResult.created_archives ?? 0}
            {(importResult.errors || []).length > 0 && (
              <ul className="mt-1 max-h-32 overflow-auto text-error">
                {importResult.errors.slice(0, 20).map((er, i) => <li key={i}>{er.sheet} 第 {er.row} 行 {er.column}：{er.message}</li>)}
              </ul>
            )}
          </div>
        )}
      </div>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} rows={req.data?.items || []} columns={[
          { key: "name", title: "用户", render: (r) => <><div>{r.real_name} {r.is_demo && <span className="badge badge-outline badge-xs">演示</span>}</div><div className="mono text-xs text-base-content/50">{r.username}</div></> },
          { key: "org", title: "组织", render: (r) => r.org_name },
          { key: "roles", title: "角色", render: (r) => <span className="text-xs">{(r.roles || []).map((x) => roleName(meta, x.role || x)).join("、")}</span> },
          { key: "st", title: "状态", render: (r) => (r.is_active === false ? "停用" : r.locked_until ? "锁定" : "正常") },
          { key: "login", title: "最近登录", render: (r) => <span className="text-xs">{fmtDateTime(r.last_login_at)}</span> },
          { key: "op", title: "", render: (r) => (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => setEdit({ ...r, role: (r.roles || []).map((x) => x.role).join(","), is_active: r.is_active !== false })}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => reset(r)}>重置密码</button>
            </>
          ) },
        ]} />
        <Pager page={req.data?.page} pageSize={req.data?.page_size} total={req.data?.total} onPage={setPage} />
      </div>
      {secret && <div className="alert mt-3 text-sm">初始密码只显示这一次：<span className="mono font-medium">{secret}</span></div>}
      <Modal open={!!edit} title={edit?.id ? "编辑用户" : "新增用户"} onClose={() => setEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={save}>保存</button>
        </>
      }>
        {edit && (
          <div className="grid gap-2">
            {!edit.id && <input className="input input-bordered input-sm" placeholder="账号（工号/学号）" value={edit.username} onChange={(e) => setEdit({ ...edit, username: e.target.value })} />}
            <input className="input input-bordered input-sm" placeholder="姓名" value={edit.real_name || ""} onChange={(e) => setEdit({ ...edit, real_name: e.target.value })} />
            <select className="select select-bordered select-sm" value={edit.org_id || ""} onChange={(e) => setEdit({ ...edit, org_id: e.target.value })}>
              <option value="">请选择组织</option>
              {(orgs.data || []).map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}（{org.org_type}）
                </option>
              ))}
            </select>
            <select className="select select-bordered select-sm" value={(edit.role || "").split(",")[0]} onChange={(e) => setEdit({ ...edit, role: e.target.value })}>
              {ROLES.map((r) => <option key={r} value={r}>{roleName(meta, r)}</option>)}
            </select>
            {edit.id && <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="toggle toggle-sm" checked={edit.is_active !== false} onChange={(e) => setEdit({ ...edit, is_active: e.target.checked })} />启用</label>}
          </div>
        )}
      </Modal>
    </div>
  )
}
