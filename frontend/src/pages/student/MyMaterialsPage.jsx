import { useState } from "react"
import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import ChecklistPanel from "../../components/material/ChecklistPanel"
import MaterialViewer from "../../components/material/MaterialViewer"
import { Loading, ErrorState } from "../../components/common/States"
import { Modal } from "../../components/common/Modal"
import { useRequest } from "../../hooks/useRequest"
import { myArchive } from "../../api/archives"
import { deleteMaterial, listMaterials, uploadMaterial } from "../../api/materials"
import { useToast } from "../../context/ToastContext"

export default function MyMaterialsPage() {
  const toast = useToast()
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const sub = archive?.current_submission
  const editable = !sub?.id || sub.status === "DRAFT" || sub.status === "RETURNED"
  const mats = useRequest(
    () => (archive?.id ? listMaterials(archive.id, { stage_code: archive.current_stage }) : []),
    [archive?.id, archive?.current_stage],
    { immediate: !!archive?.id },
  )
  const [preview, setPreview] = useState(null)

  const onUpload = async (file, item, setProgress) => {
    await uploadMaterial(archive.id, file, {
      material_type_id: item.material_type?.id,
      stage_code: archive.current_stage,
      title: file.name,
    }, setProgress)
    toast.success("已上传，正在解析")
    mats.reload()
  }

  const remove = async (id) => {
    await deleteMaterial(id)
    toast.success("已删除")
    mats.reload()
  }

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={archiveReq.reload} />

  const groups = Array.isArray(mats.data) ? mats.data : []

  return (
    <div>
      <PageHeader
        title="我的材料"
        extra={sub?.id && <Link className="btn btn-primary btn-sm" to={`/my/self-check/${sub.id}`}>发起 AI 自查</Link>}
      >
        按当前阶段清单逐项上传。留空类型时由系统识别。
      </PageHeader>
      {!editable && <div className="alert mb-3 text-sm">材料已提交审核，如需替换请等退回后再上传新版本。</div>}
      {mats.loading && !mats.data ? <Loading /> : (
        <ChecklistPanel groups={groups} canUpload={editable} onUpload={onUpload} onPreview={setPreview} />
      )}
      <Modal open={!!preview} title={preview?.title || "预览"} onClose={() => setPreview(null)} wide footer={
        preview && (
          <>
            <Link className="btn btn-ghost btn-sm" to={`/materials/${preview.id}`}>打开详情</Link>
            {editable && <button type="button" className="btn btn-error btn-sm" onClick={() => { remove(preview.id); setPreview(null) }}>删除</button>}
          </>
        )
      }>
        {preview && <MaterialViewer materialId={preview.id} versionId={preview.current_version?.id} />}
      </Modal>
    </div>
  )
}
