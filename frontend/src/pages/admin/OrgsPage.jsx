import { useState } from "react"
import PageHeader from "../../components/layout/PageHeader"
import { Modal, ConfirmDialog } from "../../components/common/Modal"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { createOrg, deleteOrg, listOrgs, updateOrg } from "../../api/orgs"
import { useToast } from "../../context/ToastContext"

function Node({ node, depth, onEdit, onAdd, onRemove }) {
  const [open, setOpen] = useState(depth < 2)
  const children = node.children || []
  return (
    <li>
      <div className="flex items-center gap-2 py-1" style={{ paddingLeft: depth * 16 }}>
        {children.length > 0 ? (
          <button type="button" className="btn btn-ghost btn-xs" onClick={() => setOpen((v) => !v)} aria-label="展开">{open ? "−" : "+"}</button>
        ) : <span className="w-6" />}
        <span className="text-sm">{node.name}</span>
        <span className="badge badge-ghost badge-xs">{node.org_type}</span>
        {!node.is_active && <span className="badge badge-outline badge-xs">停用</span>}
        {node.is_demo && <span className="badge badge-outline badge-xs">演示</span>}
        <button type="button" className="btn btn-ghost btn-xs" onClick={() => onEdit(node)}>编辑</button>
        {node.org_type !== "BRANCH" && <button type="button" className="btn btn-ghost btn-xs" onClick={() => onAdd(node)}>下级</button>}
        <button type="button" className="btn btn-ghost btn-xs text-error" onClick={() => onRemove(node)}>删除</button>
      </div>
      {open && children.length > 0 && (
        <ul>{children.map((c) => <Node key={c.id} node={c} depth={depth + 1} onEdit={onEdit} onAdd={onAdd} onRemove={onRemove} />)}</ul>
      )}
    </li>
  )
}

const CHILD = { SCHOOL: "COLLEGE", COLLEGE: "BRANCH" }

export default function OrgsPage() {
  const toast = useToast()
  const req = useRequest(() => listOrgs({ flat: false }), [])
  const [edit, setEdit] = useState(null)
  const [remove, setRemove] = useState(null)
  const tree = Array.isArray(req.data) ? req.data : []

  const save = async () => {
    try {
      if (edit.id) await updateOrg(edit.id, { name: edit.name, code: edit.code, is_active: edit.is_active })
      else await createOrg({ parent_id: edit.parent_id, org_type: edit.org_type, name: edit.name, code: edit.code || undefined })
      toast.success("已保存")
      setEdit(null)
      req.reload()
    } catch (e) {
      toast.error(e.message || "保存失败")
    }
  }

  return (
    <div>
      <PageHeader title="组织架构" extra={<button type="button" className="btn btn-primary btn-sm" onClick={() => setEdit({ org_type: "SCHOOL", name: "", code: "", is_active: true })}>新增学校</button>} />
      {req.loading && !req.data ? <Loading /> : req.error ? <ErrorState error={req.error} onRetry={req.reload} /> : (
        <ul className="surface-card p-3">{tree.map((n) => <Node key={n.id} node={n} depth={0} onEdit={setEdit} onAdd={(parent) => setEdit({ parent_id: parent.id, org_type: CHILD[parent.org_type], name: "", code: "", is_active: true })} onRemove={setRemove} />)}</ul>
      )}
      <Modal open={!!edit} title={edit?.id ? "编辑组织" : "新增组织"} onClose={() => setEdit(null)} footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEdit(null)}>取消</button>
          <button type="button" className="btn btn-primary btn-sm" onClick={save}>保存</button>
        </>
      }>
        {edit && (
          <div className="space-y-2">
            <div className="text-xs text-base-content/50">类型 {edit.org_type}</div>
            <input className="input input-bordered input-sm w-full" placeholder="名称" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
            <input className="input input-bordered input-sm w-full" placeholder="编码" value={edit.code || ""} onChange={(e) => setEdit({ ...edit, code: e.target.value })} />
            {edit.id && <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="toggle toggle-sm" checked={edit.is_active !== false} onChange={(e) => setEdit({ ...edit, is_active: e.target.checked })} />启用</label>}
          </div>
        )}
      </Modal>
      <ConfirmDialog open={!!remove} danger title="删除组织" message={`${remove?.name || ""} 若仍有下级、用户或档案，后端会要求改为停用。`} onClose={() => setRemove(null)} onConfirm={async () => {
        try {
          await deleteOrg(remove.id)
          setRemove(null)
          req.reload()
        } catch (e) {
          toast.error(e.message || "删除失败")
        }
      }} />
    </div>
  )
}
