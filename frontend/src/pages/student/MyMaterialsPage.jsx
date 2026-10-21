import { useState } from "react"
import { Link } from "react-router-dom"
import { Clock3, FileCheck2, ListChecks } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import ChecklistPanel from "../../components/material/ChecklistPanel"
import MaterialViewer from "../../components/material/MaterialViewer"
import { Loading, ErrorState } from "../../components/common/States"
import { ConfirmDialog, Modal } from "../../components/common/Modal"
import { StatusBadge } from "../../components/common/Badges"
import { useRequest } from "../../hooks/useRequest"
import { myArchive } from "../../api/archives"
import { deleteMaterial, listMaterials, uploadMaterial } from "../../api/materials"
import { useToast } from "../../context/ToastContext"

export default function MyMaterialsPage() {
  const toast = useToast()
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const sub = archive?.current_submission
  const editable = Boolean(sub?.id) && (sub.status === "DRAFT" || sub.status === "RETURNED")
  const mats = useRequest(
    () => (archive?.id ? listMaterials(archive.id, { stage_code: archive.current_stage }) : []),
    [archive?.id, archive?.current_stage],
    { immediate: !!archive?.id },
  )
  const [preview, setPreview] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [filter, setFilter] = useState("all")

  const onUpload = async (file, item, setProgress) => {
    if (!editable || !archive?.id) throw new Error("当前提交状态不可上传材料")
    setUploading(true)
    try {
      await uploadMaterial(archive.id, file, {
        material_type_id: item.material_type?.id,
        stage_code: archive.current_stage,
        title: file.name,
      }, setProgress)
      try {
        await mats.reload()
        toast.success("材料已上传，后台正在解析")
      } catch {
        toast.info("材料已上传，但列表刷新失败；请刷新页面查看")
      }
    } catch (error) {
      toast.error(error.message || "材料上传失败，请稍后重试")
      throw error
    } finally {
      setUploading(false)
    }
  }

  const remove = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await deleteMaterial(pendingDelete.id)
      toast.success("材料已删除")
      setPendingDelete(null)
      try {
        await mats.reload()
      } catch {
        toast.info("删除已完成，但列表刷新失败；请重新加载页面")
      }
    } catch (error) {
      toast.error(error.message || "删除失败，请稍后重试")
    } finally {
      setDeleting(false)
    }
  }

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={archiveReq.reload} />

  const groups = Array.isArray(mats.data) ? mats.data : []
  const checklist = groups.flatMap((group) => group.checklist || [])
  const missingRequired = checklist.reduce((sum, item) => sum + (item.required ? item.missing_count || 0 : 0), 0)
  const expectedCount = checklist.reduce((sum, item) => sum + (Number.isFinite(Number(item.expected_count)) ? Number(item.expected_count) : 0), 0)
  const uploadedCount = checklist.reduce((sum, item) => sum + (Number(item.actual_count) || 0), 0)
  const completion = expectedCount ? Math.min(100, Math.round((uploadedCount / expectedCount) * 100)) : 0
  const materialCount = checklist.reduce((sum, item) => sum + (item.materials || []).length, 0)
    + groups.reduce((sum, group) => sum + (group.unclassified || []).length + (group.extra || []).length, 0)

  return (
    <div>
      <PageHeader
        title="我的材料"
        extra={(
          <div className="flex flex-wrap gap-2">
            <Link className="btn btn-ghost btn-sm gap-2" to="/my/progress"><Clock3 size={15} strokeWidth={1.8} />发展进度</Link>
            {sub?.id && <Link className="btn btn-ghost btn-sm gap-2" to="/my/rectification"><ListChecks size={15} strokeWidth={1.8} />整改中心</Link>}
            {sub?.id && <Link className="btn btn-primary btn-sm gap-2" to={`/my/self-check/${sub.id}`}><FileCheck2 size={15} strokeWidth={1.8} />AI 自查与提交</Link>}
          </div>
        )}
      >
        {archive?.stage_name || `阶段 ${archive?.current_stage || "—"}`} · 按清单逐项上传；支持 PDF、JPG、PNG、DOCX，单文件不超过 20 MB。
      </PageHeader>
      <section className="surface-card mb-4 space-y-3 p-3 text-sm">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <div><span className="text-base-content/55">材料数：</span><strong>{materialCount}</strong></div>
          <div><span className="text-base-content/55">必需材料待补：</span><strong className={missingRequired ? "text-error" : "text-success"}>{missingRequired}</strong></div>
          <div className="flex items-center gap-2"><span className="text-base-content/55">提交状态：</span><StatusBadge code={sub?.status} /></div>
        </div>
        {expectedCount > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs text-base-content/60">清单完成度 {uploadedCount}/{expectedCount}</span>
            <progress className="progress progress-primary w-40" value={completion} max="100" aria-label={`材料清单完成度 ${completion}%`} />
            <span className="mono text-xs text-base-content/60">{completion}%</span>
          </div>
        )}
      </section>
      {!sub?.id && <div className="alert alert-warning mb-3 text-sm">当前档案没有可上传的提交包，请联系支部管理员检查档案阶段配置。</div>}
      {sub?.id && !editable && <div className="alert alert-info mb-3 text-sm">材料当前处于审核流程中，暂不可修改。若需补充或替换，请等待审核退回后再操作。</div>}
      {mats.error ? <ErrorState error={mats.error} onRetry={mats.reload} /> : mats.loading && !mats.data ? <Loading /> : (
        <>
          <div className="mb-3 flex flex-wrap items-center gap-2" aria-label="材料筛选">
            {[ ["all", "全部清单"], ["missing", "待补材料"], ["uploaded", "已有材料"] ].map(([value, label]) => (
              <button key={value} type="button" className={`btn btn-xs ${filter === value ? "btn-primary" : "btn-ghost"}`} aria-pressed={filter === value} onClick={() => setFilter(value)}>
                {label}
              </button>
            ))}
          </div>
          <ChecklistPanel groups={groups} canUpload={editable} uploadDisabled={uploading} filter={filter} onUpload={onUpload} onPreview={setPreview} />
        </>
      )}
      <Modal open={!!preview} title={preview?.title || "预览"} onClose={() => setPreview(null)} wide footer={
        preview && (
          <>
            <Link className="btn btn-ghost btn-sm" to={`/materials/${preview.id}`}>打开详情</Link>
            {editable && <button type="button" className="btn btn-error btn-sm" onClick={() => { setPendingDelete(preview); setPreview(null) }}>删除材料</button>}
          </>
        )
      }>
        {preview && <MaterialViewer materialId={preview.id} versionId={preview.current_version?.id} />}
      </Modal>
      <ConfirmDialog
        open={!!pendingDelete}
        title="删除这份材料？"
        message={`将删除“${pendingDelete?.title || `材料 #${pendingDelete?.id}`}”。删除后它会从当前阶段清单中移除，确定继续吗？`}
        confirmText="确认删除"
        danger
        busy={deleting}
        onClose={() => { if (!deleting) setPendingDelete(null) }}
        onConfirm={remove}
      />
    </div>
  )
}
