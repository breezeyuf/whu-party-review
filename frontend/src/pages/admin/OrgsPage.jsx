import { useState } from "react"
import { useAuth } from "../../context/AuthContext"
import PageHeader from "../../components/layout/PageHeader"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { Loading, ErrorState, EmptyState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { createOrg, deleteOrg, listOrgs, updateOrg } from "../../api/orgs"
import { useToast } from "../../context/ToastContext"

function Node({ node, depth, onEdit, onAdd, onRemove, canEdit, canDelete }) {
  const [open, setOpen] = useState(depth < 2)
  const children = node.children || []
  return (
    <li>
      <div className="flex flex-wrap items-center gap-2 py-2" style={{ paddingInlineStart: `${depth}rem` }}>
        {children.length > 0 ? (
          <button type="button" className="btn btn-ghost btn-xs" onClick={() => setOpen((v) => !v)} aria-label={`${open ? "收起" : "展开"}${node.name}`} aria-expanded={open}>{open ? "−" : "+"}</button>
        ) : <span className="w-6" />}
        <span className="text-sm">{node.name}</span>
        <span className="badge badge-ghost badge-xs">{ORG_TYPE_NAME[node.org_type] || node.org_type}</span>
        {!node.is_active && <span className="badge badge-outline badge-xs">停用</span>}
        {node.is_demo && <span className="badge badge-outline badge-xs">演示</span>}
        {canEdit && <button type="button" className="btn btn-ghost btn-xs" onClick={() => onEdit(node)}>编辑</button>}
        {canEdit && node.org_type !== "BRANCH" && <button type="button" className="btn btn-ghost btn-xs" onClick={() => onAdd(node)}>下级</button>}
        {canDelete && <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => onRemove(node)}>删除</button>}
      </div>
      {open && children.length > 0 && (
        <ul>{children.map((c) => <Node key={c.id} node={c} depth={depth + 1} onEdit={onEdit} onAdd={onAdd} onRemove={onRemove} canEdit={canEdit} canDelete={canDelete} />)}</ul>
      )}
    </li>
  )
}

const CHILD = { SCHOOL: "COLLEGE", COLLEGE: "BRANCH" }
const ORG_TYPE_NAME = { SCHOOL: "学校", COLLEGE: "学院", BRANCH: "党支部" }

export default function OrgsPage() {
  const toast = useToast()
  const { activeRole } = useAuth()
  const canEdit = ["SYS_ADMIN", "ORG_ADMIN"].includes(activeRole?.role)
  const canDelete = activeRole?.role === "SYS_ADMIN"
  const req = useRequest(() => listOrgs({ flat: false, include_inactive: true }), [])
  const [edit, setEdit] = useState(null)
  const [remove, setRemove] = useState(null)
  const [saving, setSaving] = useState(false)
  const [removing, setRemoving] = useState(false)
  const tree = Array.isArray(req.data) ? req.data : []

  const save = async () => {
    if (saving) return
    if (!String(edit?.name || "").trim()) { toast.error("请填写组织名称"); return }
    setSaving(true)
    try {
      if (edit.id) await updateOrg(edit.id, { name: edit.name.trim(), code: edit.code?.trim(), is_active: edit.is_active })
      else await createOrg({ parent_id: edit.parent_id, org_type: edit.org_type, name: edit.name.trim(), code: edit.code?.trim() || undefined })
      toast.success("已保存")
      setEdit(null)
      req.reload().catch((e) => toast.error(`组织已保存，但列表刷新失败：${e.message || "请重试"}`))
    } catch (e) {
      toast.error(e.message || "保存失败")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PageHeader title="组织架构" extra={canEdit && <button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ org_type: "SCHOOL", name: "", code: "", is_active: true })}>新增学校</button>} />
      {req.loading && !req.data ? <Loading label="组织架构" /> : req.error ? <ErrorState error={req.error} onRetry={req.reload} /> : !tree.length ? <EmptyState title="还没有组织" hint={canEdit ? "点击右上角“新增学校”开始维护组织架构。" : "当前暂无可查看的组织。"} /> : (
        <ul className="surface-card p-3">{tree.map((n) => <Node key={n.id} node={n} depth={0} onEdit={setEdit} onAdd={(parent) => setEdit({ parent_id: parent.id, org_type: CHILD[parent.org_type], name: "", code: "", is_active: true })} onRemove={setRemove} canEdit={canEdit} canDelete={canDelete} />)}</ul>
      )}
      <Modal open={!!edit} title={edit?.id ? "编辑组织" : "新增组织"} onClose={() => { if (!saving) setEdit(null) }} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" disabled={saving} onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" disabled={saving} onClick={save}>{saving ? "保存中…" : "保存"}</button>
        </>
      }>
        {edit && (
          <fieldset disabled={saving} className="space-y-2">
            <div className="text-xs text-base-content/50">组织类型：{ORG_TYPE_NAME[edit.org_type] || edit.org_type}</div>
            <input className="input input-bordered input-sm w-full" aria-label="组织名称" placeholder="名称" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
            <input className="input input-bordered input-sm w-full" aria-label="组织编码" placeholder="编码" value={edit.code || ""} onChange={(e) => setEdit({ ...edit, code: e.target.value })} />
            {edit.id && <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="toggle toggle-sm" checked={edit.is_active !== false} onChange={(e) => setEdit({ ...edit, is_active: e.target.checked })} />启用</label>}
          </fieldset>
        )}
      </Modal>
      <ConfirmDialog open={!!remove} danger busy={removing} title="删除组织" message={`${remove?.name || ""} 若仍有下级、用户或档案，后端会要求改为停用。`} onClose={() => { if (!removing) setRemove(null) }} onConfirm={async () => {
        if (removing) return
        setRemoving(true)
        try {
          await deleteOrg(remove.id)
          setRemove(null)
          toast.success("组织已删除")
          req.reload().catch((e) => toast.error(`删除成功，但列表刷新失败：${e.message || "请重试"}`))
        } catch (e) {
          toast.error(e.message || "删除失败")
        } finally {
          setRemoving(false)
        }
      }} />
    </div>
  )
}
