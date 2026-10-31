import { useEffect, useRef, useState } from "react"
import { Link } from "react-router-dom"
import { Clock3, FileCheck2, ListChecks } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import FileUploader from "../../components/common/FileUploader"
import { getMeta } from "../../api/meta"
import ChecklistPanel from "../../components/material/ChecklistPanel"
import MaterialViewer from "../../components/material/MaterialViewer"
import { Loading, ErrorState } from "../../components/common/States"
import { ConfirmDialog, Modal } from "../../components/common/Modal"
import { StatusBadge } from "../../components/common/Badges"
import { useRequest } from "../../hooks/useRequest"
import { myArchive } from "../../api/archives"
import { deleteMaterial, listMaterials, uploadMaterial } from "../../api/materials"
import { useToast } from "../../context/ToastContext"
import StudentTaskProgress from "../../utils/student/StudentTaskProgress"
import { pendingParseCount, refreshStudentRequests, studentMaterials } from "../../utils/studentWorkflow"

export default function MyMaterialsPage() {
  const toast = useToast()
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const sub = archive?.current_submission
  const editable = !!archive?.id && (!sub?.id || sub.status === "DRAFT" || sub.status === "RETURNED")
  const mats = useRequest(
    () => (archive?.id ? listMaterials(archive.id, { stage_code: archive.current_stage }) : []),
    [archive?.id, archive?.current_stage],
    { immediate: !!archive?.id },
  )
  const types = useRequest(getMeta, [editable], { immediate: editable })
  const [extraType, setExtraType] = useState("")
  const [preview, setPreview] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [jobs, setJobs] = useState([])
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState("")
  const deleteLock = useRef(false)
  const pending = pendingParseCount(Array.isArray(mats.data) ? mats.data : [])

  // Recover pending parsing when the user returns to this page without the
  // original upload response (and therefore without its job id).
  useEffect(() => {
    if (!pending || mats.loading) return undefined
    const timer = setTimeout(() => mats.reload().catch(() => {}), 2000)
    return () => clearTimeout(timer)
  }, [pending, mats.loading, mats.reload])

  const onUpload = async (file, item, setProgress) => {
    if (!editable) throw new Error("当前状态不可上传材料")
    const res = await uploadMaterial(archive.id, file, {
      material_type_id: item.material_type?.id,
      stage_code: archive.current_stage,
      title: file.name,
    }, setProgress)
    if (res?.parse_job_id) setJobs((previous) => [...new Set([...previous, res.parse_job_id])])
    toast.success("已上传，正在解析")
    refreshStudentRequests(mats, archiveReq)
  }

  const remove = async (id) => {
    if (deleteLock.current || !editable) return
    deleteLock.current = true
    setDeleting(true)
    setError("")
    try {
      await deleteMaterial(id)
      toast.success("已删除")
      setPreview(null)
      refreshStudentRequests(mats, archiveReq)
      return true
    } catch (e) { setError(e.message || "删除失败"); return false }
    finally { setDeleting(false); deleteLock.current = false }
  }

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={archiveReq.reload} />

  const groups = Array.isArray(mats.data) ? mats.data : []
  const currentPreview = studentMaterials(groups).find((material) => material.id === preview?.id) || preview

  return (
    <div>
      <PageHeader
        title="我的材料"
        extra={(
          <div className="flex flex-wrap gap-2">
            <Link className="btn btn-ghost btn-sm gap-2" to="/my/progress"><Clock3 size={15} strokeWidth={1.8} />我的发展进度</Link>
            {sub?.id && <Link className="btn btn-ghost btn-sm gap-2" to="/my/rectification"><ListChecks size={15} strokeWidth={1.8} />整改中心</Link>}
            {sub?.id && <Link className={`btn ${editable ? "btn-primary" : "btn-outline"} btn-sm gap-2`} to={`/my/self-check/${sub.id}`}><FileCheck2 size={15} strokeWidth={1.8} />{editable ? "AI 自查与提交" : "自查报告"}</Link>}
          </div>
        )}
      >
        {archive?.stage_name || `阶段 ${archive?.current_stage || "—"}`} · {editable ? "按清单逐项上传；支持 PDF、JPG、PNG、DOCX，单文件不超过 20 MB。" : "按清单查看已提交材料与自查报告。"}
      </PageHeader>
      <div className="surface-card mb-3 flex flex-wrap items-center justify-between gap-2 p-3 text-sm" role="status">
        <div className="flex flex-wrap items-center gap-2">{sub?.status && <StatusBadge code={sub.status} />}<span className="text-base-content/65">{sub?.status === "FILED" ? "本阶段已备案，材料仅供查看。" : sub?.status === "RETURNED" ? "按审核意见补充材料，再到整改中心回复并重新提交。" : editable ? "材料准备完成后，发起自查并核对结果。" : "材料已提交审核，当前仅可查看；如需替换，请等待退回后上传新版本。"}</span></div>
        {sub?.status === "RETURNED" && <Link className="btn btn-outline btn-sm" to="/my/rectification">去整改</Link>}
      </div>
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {pending > 0 && <div className="alert alert-info mb-3 text-sm">{pending} 份材料正在解析，结果会自动刷新。解析完成后再发起自查。</div>}
      {jobs.map((jobId) => <div key={jobId} className="mb-3"><StudentTaskProgress jobId={jobId} onDone={() => refreshStudentRequests(mats, archiveReq)} /></div>)}
      {mats.loading && !mats.data ? <Loading /> : mats.error ? <ErrorState error={mats.error} onRetry={() => mats.reload().catch(() => {})} /> : (
        <ChecklistPanel groups={groups} canUpload={editable} onUpload={onUpload} onPreview={setPreview} onDelete={setPendingDelete} uploadDisabled={deleting} />
      )}
      {editable && <section className="surface-card mt-4 space-y-3 p-4" aria-label="补充材料上传">
        <h2 className="text-sm font-semibold">上传补充材料</h2>
        <p className="text-xs text-base-content/65">清单外的材料也可在这里上传；删除文件后，此入口仍保留。补充材料不替代必交材料。</p>
        {types.error && <ErrorState error={types.error} onRetry={types.reload} />}
        <label className="form-control max-w-sm text-xs">材料类型<select aria-label="补充材料类型" className="select select-bordered select-sm mt-1" value={extraType} disabled={deleting} onChange={e => setExtraType(e.target.value)}>
          <option value="">自动识别类型</option>
          {(types.data?.material_types || []).filter(t => !t.stage_codes?.length || t.stage_codes.map(Number).includes(Number(archive.current_stage))).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select></label>
        <FileUploader compact buttonClassName="btn-outline" accept=".pdf,.jpg,.jpeg,.png,.docx" label="上传补充材料" hint="PDF / JPG / PNG / DOCX，单文件不超过 20 MB" disabled={deleting} onFile={(file, progress) => onUpload(file, { material_type: { id: extraType ? Number(extraType) : undefined } }, progress)} />
      </section>}
      <Modal open={!!preview} title={preview?.title || "预览"} onClose={() => setPreview(null)} wide footer={
        preview && (
          <>
            <Link className="btn btn-ghost btn-sm" to={`/materials/${preview.id}`}>打开详情</Link>
            {editable && <button type="button" className="btn btn-error btn-sm" disabled={deleting} onClick={() => setPendingDelete(preview)}>{deleting ? "删除中…" : "删除"}</button>}
          </>
        )
      }>
        {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
        {currentPreview && <MaterialViewer key={`${currentPreview.id}-${currentPreview.current_version?.id}-${currentPreview.current_version?.parse_status}`} materialId={currentPreview.id} versionId={currentPreview.current_version?.id} />}
      </Modal>
      <ConfirmDialog
        open={!!pendingDelete}
        title="删除这份材料？"
        message={`将删除“${pendingDelete?.title || `材料 #${pendingDelete?.id}`}”。删除后它会从当前阶段清单中移除，确定继续吗？`}
        confirmText="确认删除"
        danger
        busy={deleting}
        onClose={() => { if (!deleting) setPendingDelete(null) }}
        onConfirm={async () => {
          if (!pendingDelete) return
          if (await remove(pendingDelete.id)) setPendingDelete(null)
        }}
      />
    </div>
  )
}
