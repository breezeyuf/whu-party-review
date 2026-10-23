import { useEffect, useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import FilterBar from "../../components/common/FilterBar"
import DataTable, { Pager } from "../../components/common/DataTable"
import { Modal } from "../../components/common/Modal"
import { usePagination } from "../../hooks/usePagination"
import { useRequest } from "../../hooks/useRequest"
import { createUser, downloadImportPasswords, importTemplate, importUsers, listUsers, resetPassword, updateUser } from "../../api/users"
import { saveBlob } from "../../api/client"
import { listBatches } from "../../api/batches"
import { listOrgs } from "../../api/orgs"
import { roleName, fmtDateTime } from "../../utils/format"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"

const ROLES = ["STUDENT", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN", "SYS_ADMIN"]
const ORG_TYPE_NAMES = { SCHOOL: "学校", COLLEGE: "学院", BRANCH: "党支部" }
const formatImportError = (error) => {
  const location = [error.sheet, error.row ? `第 ${error.row} 行` : "", error.column].filter(Boolean).join(" ")
  return `${location ? `${location}：` : ""}${error.message || "未提供错误详情"}`
}

export default function UsersPage() {
  const meta = useMeta()
  const toast = useToast()
  const { query, setQuery, setPage } = usePagination()
  const req = useRequest(() => listUsers(query), [JSON.stringify(query)])
  const batches = useRequest(() => listBatches({ page_size: 20 }), [])
  const orgs = useRequest(() => listOrgs({ flat: true }), [])
  const [edit, setEdit] = useState(null)
  const [saving, setSaving] = useState(false)
  const [resetTarget, setResetTarget] = useState(null)
  const [resetting, setResetting] = useState(false)
  const [statusConfirm, setStatusConfirm] = useState(false)
  const [formError, setFormError] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [secret, setSecret] = useState("")
  const [importResult, setImportResult] = useState(null)
  const [importing, setImporting] = useState(false)
  const [downloadingPasswords, setDownloadingPasswords] = useState(false)
  const [downloadingTemplate, setDownloadingTemplate] = useState(false)
  const [pendingImportFile, setPendingImportFile] = useState(null)
  const [batchId, setBatchId] = useState("")
  const [searchTerm, setSearchTerm] = useState(query.q || "")

  useEffect(() => {
    setSearchTerm(query.q || "")
  }, [query.q])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (searchTerm !== (query.q || "")) setQuery({ q: searchTerm })
    }, 300)
    return () => window.clearTimeout(timer)
  }, [searchTerm, query.q, setQuery])

  const save = async (confirmedStatusChange = false) => {
    const username = String(edit.username || "").trim()
    const realName = String(edit.real_name || "").trim()
    const orgId = Number(edit.org_id)
    const role = String(edit.role || "").trim()
    setFieldErrors({})
    if (!edit.id && !username) {
      setFieldErrors({ username: "请填写账号（工号或学号）" })
      return
    }
    if (!edit.id && username.length > 100) {
      setFieldErrors({ username: "账号不能超过 100 个字符" })
      return
    }
    if (!realName) {
      setFieldErrors({ real_name: "请填写姓名" })
      return
    }
    if (!orgId || !Number.isInteger(orgId)) {
      setFieldErrors({ org_id: "请选择有效组织" })
      return
    }
    if (!role) {
      setFieldErrors({ role: "请选择角色" })
      return
    }
    if (orgs.loading) {
      setFormError("组织列表正在加载，请稍后再保存")
      return
    }
    if (orgs.error || !(orgs.data || []).some((org) => Number(org.id) === orgId)) {
      setFormError(orgs.error ? "组织列表加载失败，请点击重试后再保存" : "所选组织已不可用，请重新选择")
      return
    }
    if (edit.id && edit.is_active !== edit.original_is_active && !confirmedStatusChange) {
      setStatusConfirm(true)
      return
    }
    setFormError("")
    setSaving(true)
    const roles = [{ role, org_id: orgId }]
    try {
      if (edit.id) {
        await updateUser(edit.id, { real_name: realName, org_id: orgId, roles, is_active: edit.is_active !== false })
        toast.success("已更新")
        setStatusConfirm(false)
        setEdit(null)
      } else {
        const res = await createUser({ username, real_name: realName, org_id: orgId, roles })
        setSecret(res.initial_password || "")
        toast.success("用户已创建")
        setEdit(null)
      }
      req.reload().catch(() => {})
    } catch (e) {
      if (!edit.id && e.message?.includes("用户名已存在")) {
        setFieldErrors({ username: "该账号已存在，请检查工号/学号后重试" })
        setFormError("")
      } else if (e.message?.includes("组织不存在") || e.message?.includes("无权调整所属组织")) {
        setFieldErrors({ org_id: e.message })
        setFormError("")
      } else if (e.message?.includes("不能授予")) {
        setFieldErrors({ role: e.message })
        setFormError("")
      } else {
        setFormError(e.message || "保存失败，请稍后重试")
      }
    } finally {
      setSaving(false)
    }
  }

  const reset = async () => {
    if (!resetTarget || resetting) return
    setResetting(true)
    try {
      const res = await resetPassword(resetTarget.id)
      setSecret(res.initial_password || "")
      setResetTarget(null)
      toast.success("密码已重置")
    } catch (e) {
      toast.error(e.message || "重置失败")
    } finally {
      setResetting(false)
    }
  }

  const copyFilePassword = async () => {
    const password = importResult?.initial_passwords_file?.password
    if (!password) return
    try {
      await navigator.clipboard.writeText(password)
      toast.success("文件打开口令已复制")
    } catch {
      toast.error("复制失败，请手动选中并复制打开口令")
    }
  }

  const downloadPasswords = async () => {
    const file = importResult?.initial_passwords_file
    if (!file || file.downloaded || downloadingPasswords) return
    setDownloadingPasswords(true)
    try {
      const result = await downloadImportPasswords(file.id)
      saveBlob(result)
      setImportResult((current) => current?.initial_passwords_file?.id === file.id
        ? { ...current, initial_passwords_file: { ...file, downloaded: true } } : current)
      toast.success("密码文件已下载，请使用显示的口令打开")
    } catch (e) {
      toast.error(e.message || "密码文件下载失败")
    } finally {
      setDownloadingPasswords(false)
    }
  }

  const copySecret = async () => {
    if (!secret) return
    try {
      await navigator.clipboard.writeText(secret)
      toast.success("临时密码已复制")
    } catch {
      toast.error("浏览器不允许自动复制，请手动选中密码复制")
    }
  }

  const doImport = async (file, dryRun) => {
    if (importing || downloadingPasswords) return
    const fileProblem = !file.name.toLowerCase().endsWith(".xlsx")
      ? "请选择 .xlsx 格式的 Excel 文件"
      : file.size > 10 * 1024 * 1024
        ? "文件超过 10 MB，请压缩或拆分后再导入"
        : ""
    if (fileProblem) {
      setImportResult({ total: 0, valid: 0, created_users: 0, created_archives: 0, errors: [{ message: fileProblem }], dryRun, failed: true })
      return
    }
    setImporting(true)
    setImportResult(null)
    try {
      const res = await importUsers(file, { dryRun, batchId: batchId || undefined })
      setImportResult({ ...res, dryRun, failed: false })
      if (!dryRun) req.reload().catch(() => {})
    } catch (e) {
      // 导入失败（含整体回滚）时展示错误明细
      const errs = e.data?.errors || [{ message: e.message || "导入失败" }]
      setImportResult({ total: 0, valid: 0, created_users: 0, created_archives: 0, errors: errs, dryRun, failed: true })
      toast.error(e.message || "导入失败")
    } finally {
      setImporting(false)
    }
  }

  const downloadTemplate = async () => {
    if (downloadingTemplate) return
    setDownloadingTemplate(true)
    try {
      saveBlob(await importTemplate())
      toast.success("导入模板下载已开始")
    } catch (e) {
      toast.error(e.message || "模板下载失败，请稍后重试")
    } finally {
      setDownloadingTemplate(false)
    }
  }

  const confirmFormalImport = () => {
    if (!pendingImportFile || importing) return
    const file = pendingImportFile
    setPendingImportFile(null)
    doImport(file, false)
  }

  return (
    <div>
      <PageHeader title="用户管理" extra={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={downloadTemplate} disabled={downloadingTemplate}>
            {downloadingTemplate && <span className="loading loading-spinner loading-xs" />}
            {downloadingTemplate ? "模板准备中…" : "下载导入模板"}
          </button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => { setSecret(""); setFormError(""); setFieldErrors({}); setEdit({ username: "", real_name: "", org_id: "", role: "STUDENT", is_active: true }) }}>新增用户</button>
        </>
      } />
      <FilterBar values={{ ...query, q: searchTerm }} onChange={(patch) => {
        if (Object.prototype.hasOwnProperty.call(patch, "q")) setSearchTerm(patch.q)
        else setQuery(patch)
      }} onReset={() => { setSearchTerm(""); setQuery({ q: "", role: "", org_id: "", is_active: "" }) }} fields={[
        { key: "q", label: "姓名 / 账号" },
        { key: "role", label: "角色", type: "select", metaKey: "roles" },
        { key: "org_id", label: "所属组织", type: "select", placeholder: "全部组织", options: (orgs.data || []).map((org) => ({ id: org.id, name: `${org.name}（${ORG_TYPE_NAMES[org.org_type] || org.org_type}）` })) },
        { key: "is_active", label: "状态", type: "select", options: [{ code: "true", name: "启用" }, { code: "false", name: "停用" }] },
      ]} />
      <div className="surface-card mb-4 p-3 text-sm">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="text-xs text-base-content/60">Excel 导入</span>
          <select className="select select-bordered select-xs" value={batchId} onChange={(e) => setBatchId(e.target.value)} disabled={importing}>
            <option value="">未指定批次</option>
            {(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
          <label className={`btn btn-outline btn-xs ${importing ? "pointer-events-none opacity-50" : ""}`} aria-disabled={importing}>{importing ? "处理中…" : "预校验"}<input type="file" accept=".xlsx" className="hidden" disabled={importing} onChange={(e) => { const file = e.target.files?.[0]; e.target.value = ""; if (file) doImport(file, true) }} /></label>
          <label className={`btn btn-primary btn-xs ${importing ? "pointer-events-none opacity-50" : ""}`} aria-disabled={importing}>{importing ? "处理中…" : "正式导入"}<input type="file" accept=".xlsx" className="hidden" disabled={importing} onChange={(e) => { const file = e.target.files?.[0]; e.target.value = ""; if (file) { setImportResult(null); setPendingImportFile(file) } }} /></label>
          {importing && <span className="flex items-center gap-2 text-xs text-base-content/60" role="status"><span className="loading loading-spinner loading-xs" />正在上传并校验文件，请勿关闭页面</span>}
        </div>
        {importResult && (
          <div className={`rounded-lg p-3 text-xs ${importResult.failed || (importResult.errors || []).length ? "bg-error/10" : "bg-base-200/60"}`} role="status">
            <div className="mb-1 flex items-center justify-between gap-2 font-medium">
              <span>{importResult.failed
                ? (importResult.dryRun ? "预校验失败" : "正式导入失败，本次导入未完成")
                : importResult.dryRun
                  ? ((importResult.errors || []).length ? "预校验完成，发现问题（未写入数据）" : "预校验通过（未写入数据）")
                  : "正式导入完成"}</span>
              <button type="button" className="btn btn-ghost btn-xs" disabled={downloadingPasswords} onClick={() => setImportResult(null)}>清除结果</button>
            </div>
            <div>共 {importResult.total} 行，有效 {importResult.valid}，新建用户 {importResult.created_users ?? 0}，档案 {importResult.created_archives ?? 0}</div>
            {!importResult.dryRun && !importResult.failed && importResult.initial_passwords_file && (
              <div className="alert alert-warning mt-3 block text-xs">
                <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                  <span className="font-medium">新账号密码已生成加密 Excel，可在 24 小时内下载一次。</span>
                  <button type="button" className="btn btn-outline btn-xs" onClick={downloadPasswords} disabled={downloadingPasswords || importResult.initial_passwords_file.downloaded}>
                    {importResult.initial_passwords_file.downloaded ? "已下载" : downloadingPasswords ? "正在下载…" : "下载密码文件"}
                  </button>
                </div>
                <p>文件打开口令（仅本次显示）：<span className="mono select-all">{importResult.initial_passwords_file.password}</span>
                  <button type="button" className="btn btn-ghost btn-xs" onClick={copyFilePassword}>复制口令</button></p>
              </div>
            )}
            {(importResult.errors || []).length > 0 && (
              <div className="mt-2 text-error">发现 {importResult.errors.length} 个问题，最多显示 20 条：<ul className="mt-1 max-h-32 overflow-auto">
                {importResult.errors.slice(0, 20).map((er, i) => <li key={i}>{formatImportError(er)}</li>)}
              </ul></div>
            )}
          </div>
        )}
      </div>
      <div className="surface-card p-2">
        <DataTable loading={req.loading} error={req.error} onRetry={req.reload} rows={req.data?.items || []} empty={query.q || query.role || query.org_id || query.is_active ? "没有符合条件的用户" : "暂无用户"} columns={[
          { key: "name", title: "用户", render: (r) => <><div>{r.real_name} {r.is_demo && <span className="badge badge-outline badge-xs">演示</span>}</div><div className="mono text-xs text-base-content/50">{r.username}</div></> },
          { key: "org", title: "组织", render: (r) => r.org_name },
          { key: "roles", title: "角色", render: (r) => <span className="text-xs">{(r.roles || []).map((x) => roleName(meta, x.role || x)).join("、")}</span> },
          { key: "st", title: "状态", render: (r) => r.is_active === false
            ? <span className="badge badge-error badge-outline badge-sm">已停用</span>
            : r.locked_until
              ? <span className="badge badge-warning badge-outline badge-sm" title={`锁定至 ${fmtDateTime(r.locked_until)}`}>登录锁定</span>
              : <span className="badge badge-success badge-outline badge-sm">正常</span> },
          { key: "login", title: "最近登录", render: (r) => <span className="text-xs">{fmtDateTime(r.last_login_at)}</span> },
          { key: "op", title: "", render: (r) => (
            <>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => { setFormError(""); setFieldErrors({}); setEdit({ ...r, role: (r.roles || []).map((x) => x.role).join(","), is_active: r.is_active !== false, original_is_active: r.is_active !== false }) }}>编辑</button>
              <button type="button" className="btn btn-ghost btn-xs" onClick={() => { setSecret(""); setResetTarget(r) }}>重置密码</button>
            </>
          ) },
        ]} />
        {!req.error && <Pager
          page={req.data?.page ?? query.page}
          pageSize={req.data?.page_size ?? query.page_size}
          total={req.data?.total}
          onPage={setPage}
          onPageSize={(page_size) => setQuery({ page_size })}
        />}
      </div>
      {secret && <div className="alert mt-3 flex flex-wrap items-center justify-between gap-3 text-sm" role="status"><span>初始密码只显示这一次：<span className="mono font-medium select-all">{secret}</span></span><div className="flex items-center gap-1"><button type="button" className="btn btn-outline btn-xs" onClick={copySecret}>复制临时密码</button><button type="button" className="btn btn-ghost btn-xs" onClick={() => setSecret("")}>关闭密码提示</button></div></div>}
      <Modal open={!!pendingImportFile} title="确认正式导入" onClose={() => setPendingImportFile(null)} footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setPendingImportFile(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={confirmFormalImport}>
            确认并导入
          </button>
        </>
      )}>
        {pendingImportFile && <div className="grid gap-3">
          <div className="text-sm">文件：<span className="font-medium break-all">{pendingImportFile.name}</span></div>
          <div className="text-sm">学生档案建档批次：<span className="font-medium">{batchId ? (batches.data?.items || []).find((batch) => String(batch.id) === String(batchId))?.name || `批次 ${batchId}` : "未指定，可使用文件中的批次名称"}</span></div>
          <div className="alert alert-warning text-sm" role="alert">正式导入会创建文件中的用户/档案。新用户的初始密码通过加密 Excel 交付，文件只能下载一次，打开口令仅本次显示。建议先对同一文件执行预校验。</div>
        </div>}
      </Modal>
      <Modal open={!!resetTarget} title="确认重置密码" onClose={() => { if (!resetting) setResetTarget(null) }} footer={(
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setResetTarget(null)} disabled={resetting}>取消</button>
          <button type="button" className="btn btn-error btn-sm" onClick={reset} disabled={resetting}>
            {resetting && <span className="loading loading-spinner loading-xs" />}
            {resetting ? "正在重置…" : "确认重置密码"}
          </button>
        </>
      )}>
        {resetTarget && <div className="alert alert-warning" role="alert">
          <span>即将重置用户“{resetTarget.real_name}（{resetTarget.username}）”的密码。旧密码会立即失效，系统生成的新初始密码只显示一次。</span>
        </div>}
      </Modal>
      <Modal open={!!edit} title={statusConfirm ? (edit?.is_active === false ? "确认停用用户" : "确认启用用户") : (edit?.id ? "编辑用户" : "新增用户")} onClose={() => { if (!saving) { setStatusConfirm(false); setEdit(null) } }} footer={statusConfirm ? (
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setStatusConfirm(false)} disabled={saving}>返回修改</button>
          <button type="button" className={`btn btn-sm ${edit?.is_active === false ? "btn-error" : "btn-primary"}`} onClick={() => save(true)} disabled={saving}>
            {saving && <span className="loading loading-spinner loading-xs" />}
            {saving ? "处理中…" : (edit?.is_active === false ? "确认停用" : "确认启用")}
          </button>
        </>
      ) : (
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEdit(null)} disabled={saving}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => save()} disabled={saving || orgs.loading || !!orgs.error}>
            {saving && <span className="loading loading-spinner loading-xs" />}
            {saving ? "保存中" : "保存"}
          </button>
        </>
      )}>
        {edit && (
          statusConfirm ? (
            <div className={`alert ${edit.is_active === false ? "alert-warning" : "alert-info"}`} role="alert">
              <span>{edit.is_active === false
                ? `确定停用“${edit.real_name}（${edit.username}）”吗？停用后该用户将无法登录，已有登录会话也会失效。`
                : `确定重新启用“${edit.real_name}（${edit.username}）”吗？启用后该用户可以再次登录。`}</span>
            </div>
          ) : <div className="grid gap-2">
            {!edit.id && <label className="form-control gap-1"><span className="label-text text-xs">账号（工号/学号）</span><input className={`input input-bordered input-sm ${fieldErrors.username ? "input-error" : ""}`} placeholder="请输入账号" value={edit.username} onChange={(e) => { setEdit({ ...edit, username: e.target.value }); setFormError(""); setFieldErrors((errors) => ({ ...errors, username: "" })) }} maxLength={100} autoComplete="off" aria-invalid={!!fieldErrors.username} aria-describedby={fieldErrors.username ? "user-account-error" : undefined} />{fieldErrors.username && <span id="user-account-error" className="text-xs text-error" role="alert">{fieldErrors.username}</span>}</label>}
            <label className="form-control gap-1"><span className="label-text text-xs">姓名</span><input className={`input input-bordered input-sm ${fieldErrors.real_name ? "input-error" : ""}`} placeholder="请输入姓名" value={edit.real_name || ""} onChange={(e) => { setEdit({ ...edit, real_name: e.target.value }); setFormError(""); setFieldErrors((errors) => ({ ...errors, real_name: "" })) }} maxLength={100} autoComplete="name" aria-invalid={!!fieldErrors.real_name} aria-describedby={fieldErrors.real_name ? "user-name-error" : undefined} />{fieldErrors.real_name && <span id="user-name-error" className="text-xs text-error" role="alert">{fieldErrors.real_name}</span>}</label>
            <label className="form-control gap-1"><span className="label-text text-xs">所属组织</span><select className={`select select-bordered select-sm ${fieldErrors.org_id ? "select-error" : ""}`} value={edit.org_id || ""} onChange={(e) => { setEdit({ ...edit, org_id: e.target.value }); setFormError(""); setFieldErrors((errors) => ({ ...errors, org_id: "" })) }} disabled={orgs.loading || !!orgs.error} aria-invalid={!!fieldErrors.org_id} aria-describedby={fieldErrors.org_id ? "user-org-error" : undefined}>
              <option value="">请选择组织</option>
              {(orgs.data || []).map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}（{ORG_TYPE_NAMES[org.org_type] || org.org_type}）
                </option>
              ))}
            </select>{fieldErrors.org_id && <span id="user-org-error" className="text-xs text-error" role="alert">{fieldErrors.org_id}</span>}{orgs.loading && <span className="text-xs text-base-content/50">正在加载组织列表…</span>}{orgs.error && <span className="flex items-center gap-2 text-xs text-error">组织列表加载失败<button type="button" className="btn btn-ghost btn-xs" onClick={() => orgs.reload().catch(() => {})}>重试</button></span>}</label>
            <label className="form-control gap-1"><span className="label-text text-xs">角色</span><select className={`select select-bordered select-sm ${fieldErrors.role ? "select-error" : ""}`} value={(edit.role || "").split(",")[0]} onChange={(e) => { setEdit({ ...edit, role: e.target.value }); setFormError(""); setFieldErrors((errors) => ({ ...errors, role: "" })) }} aria-invalid={!!fieldErrors.role} aria-describedby={fieldErrors.role ? "user-role-error" : undefined}>
              {ROLES.map((r) => <option key={r} value={r}>{roleName(meta, r)}</option>)}
            </select>{fieldErrors.role && <span id="user-role-error" className="text-xs text-error" role="alert">{fieldErrors.role}</span>}</label>
            {edit.id && <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="toggle toggle-sm" checked={edit.is_active !== false} onChange={(e) => setEdit({ ...edit, is_active: e.target.checked })} />启用</label>}
            {formError && <div className="alert alert-error py-2 text-xs" role="alert">{formError}</div>}
          </div>
        )}
      </Modal>
    </div>
  )
}
