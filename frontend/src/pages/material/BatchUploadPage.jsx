import { useState } from "react"
import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FileUploader from "../../components/common/FileUploader"
import JobProgress from "../../components/common/JobProgress"
import { useJobPolling } from "../../hooks/useJobPolling"
import { assignBatch, batchUpload } from "../../api/materials"
import { listBatches } from "../../api/batches"
import { useRequest } from "../../hooks/useRequest"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"

export default function BatchUploadPage() {
  const toast = useToast()
  const meta = useMeta()
  const batches = useRequest(() => listBatches({ page_size: 50 }), [])
  const [batchId, setBatchId] = useState("")
  const [stage, setStage] = useState("")
  const [jobId, setJobId] = useState(null)
  const [assigns, setAssigns] = useState({})
  const { job } = useJobPolling(jobId)

  const items = job?.result?.items || []
  const unmatched = items.filter((it) => it.status === "UNMATCHED" || !it.matched_archive)

  const upload = async (file, setProgress) => {
    const res = await batchUpload(file, { batch_id: batchId || undefined, stage_code: stage || undefined }, setProgress)
    setJobId(res.job_id)
    toast.info("已开始归档")
  }

  const saveAssign = async () => {
    const assignments = Object.entries(assigns)
      .filter(([, v]) => v.archive_id)
      .map(([itemId, v]) => ({ item_id: Number(itemId), archive_id: Number(v.archive_id), material_type_id: v.material_type_id ? Number(v.material_type_id) : undefined }))
    if (!assignments.length) return
    await assignBatch(jobId, { assignments })
    toast.success("已指定归属")
  }

  return (
    <div>
      <PageHeader title="批量上传">
        ZIP 内按「学号_材料名」或目录归属。未匹配的文件在任务完成后人工指定。单包不超过 500 MB。
      </PageHeader>
      <div className="mb-4 flex flex-wrap gap-2">
        <select className="select select-bordered select-sm" value={batchId} onChange={(e) => setBatchId(e.target.value)}>
          <option value="">批次（可选）</option>
          {(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
        <select className="select select-bordered select-sm" value={stage} onChange={(e) => setStage(e.target.value)}>
          <option value="">阶段（可选）</option>
          {(meta.stages || []).map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
        </select>
      </div>
      <FileUploader accept=".zip" maxMb={500} label="上传 ZIP" onFile={upload} />
      {jobId && <div className="mt-4"><JobProgress job={job} /></div>}
      {items.length > 0 && (
        <div className="surface-card mt-4 overflow-x-auto">
          <table className="table table-sm">
            <thead><tr><th>文件</th><th>识别学号</th><th>归属</th><th>状态</th></tr></thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.item_id}>
                  <td className="text-xs">{it.entry_path}</td>
                  <td className="mono text-xs">{it.parsed_student_no || "—"}</td>
                  <td className="text-xs">
                    {it.matched_archive ? (
                      <Link className="link" to={`/archives/${it.matched_archive.id}`}>{it.matched_archive.real_name}</Link>
                    ) : (
                      <input
                        className="input input-bordered input-xs w-28"
                        placeholder="档案 ID"
                        value={assigns[it.item_id]?.archive_id || ""}
                        onChange={(e) => setAssigns((s) => ({ ...s, [it.item_id]: { ...s[it.item_id], archive_id: e.target.value } }))}
                      />
                    )}
                  </td>
                  <td className="text-xs">{it.status}{it.error ? ` · ${it.error}` : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {unmatched.length > 0 && job?.status && job.status !== "RUNNING" && job.status !== "QUEUED" && (
            <div className="p-3">
              <button type="button" className="btn btn-primary btn-sm" onClick={saveAssign}>保存未匹配归属</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
