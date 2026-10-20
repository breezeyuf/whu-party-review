import { useState } from "react"
import { Link } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import FileUploader from "../../components/common/FileUploader"
import { useJobPolling } from "../../hooks/useJobPolling"
import { assignBatch, batchUpload } from "../../api/materials"
import { listBatches } from "../../api/batches"
import { listArchives } from "../../api/archives"
import { useRequest } from "../../hooks/useRequest"
import { useMeta } from "../../context/MetaContext"
import { useToast } from "../../context/ToastContext"
import { batchAssignmentBody, batchDraft, JOB_TERMINAL, mergeBatchItems } from "../../utils/materialWorkflow"

const STATUS = { MATCHED: "已匹配，待确认导入", UNMATCHED: "待指定归属", IMPORTED: "已导入", SKIPPED: "已跳过", FAILED: "导入失败" }
const JOB_STATUS = { QUEUED: "排队中", RUNNING: "识别中", SUCCEEDED: "识别完成", PARTIAL: "部分失败", FAILED: "识别失败", CANCELLED: "已取消" }

export default function BatchUploadPage() {
  const toast = useToast()
  const meta = useMeta()
  const batches = useRequest(() => listBatches({ page_size: 50 }), [])
  const [batchId, setBatchId] = useState("")
  const [stage, setStage] = useState("")
  const [jobId, setJobId] = useState(null)
  const [settledItems, setSettledItems] = useState(null)
  const [assigns, setAssigns] = useState({})
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState("")
  const [search, setSearch] = useState("")
  const [query, setQuery] = useState("")
  const archives = useRequest(() => listArchives({ batch_id: batchId || undefined, q: query || undefined, page_size: 50 }), [batchId, query])
  const { job, error: pollingError } = useJobPolling(jobId, { onDone: (completed) => setSettledItems(completed.result?.items || []) })
  const currentJob = Number(job?.id) === Number(jobId) ? job : null
  const items = settledItems ?? currentJob?.result?.items ?? []
  const ready = currentJob && JOB_TERMINAL.has(currentJob.status)
  const locked = uploading || saving || (jobId && !ready)
  const body = batchAssignmentBody(items, assigns)
  const imported = items.filter((item) => item.status === "IMPORTED").length
  const failed = items.filter((item) => item.status === "FAILED").length
  const pending = items.filter((item) => !["IMPORTED", "SKIPPED"].includes(item.status)).length
  const updateDraft = (itemId, patch) => setAssigns((previous) => ({ ...previous, [itemId]: { ...previous[itemId], ...patch } }))

  const upload = async (file, setProgress) => {
    setUploading(true)
    setSaveError("")
    try {
      const res = await batchUpload(file, { batch_id: batchId || undefined, stage_code: stage || undefined }, setProgress)
      setSettledItems(null)
      setAssigns({})
      setJobId(res.job_id)
      toast.info("ZIP 已上传，正在识别文件归属")
    } finally { setUploading(false) }
  }

  const saveAssign = async () => {
    if (!body.assignments.length && !body.skip_item_ids.length) return
    setSaving(true)
    setSaveError("")
    try {
      const result = await assignBatch(jobId, body)
      setSettledItems((current) => mergeBatchItems(current ?? items, result, body.skip_item_ids))
      setAssigns((current) => {
        const next = { ...current }
        for (const item of result.items || []) if (item.status === "IMPORTED") delete next[item.item_id]
        for (const itemId of body.skip_item_ids) delete next[itemId]
        return next
      })
      const summary = `已导入 ${result.imported || 0} 个，跳过 ${result.skipped || 0} 个，失败 ${result.failed || 0} 个`
      if (result.failed) toast.error(summary)
      else toast.success(summary)
    } catch (error) { setSaveError(error.message || "确认导入失败，请重试") }
    finally { setSaving(false) }
  }

  return <div>
    <PageHeader title="批量上传">ZIP 内按「学号_材料名」或学号目录识别归属，识别后确认导入。单包不超过 500 MB。</PageHeader>
    <div className="mb-4 flex flex-wrap gap-2">
      <select aria-label="发展批次" className="select select-bordered select-sm" disabled={!!locked} value={batchId} onChange={(e) => setBatchId(e.target.value)}>
        <option value="">批次（可选）</option>
        {(batches.data?.items || []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
      </select>
      <select aria-label="发展阶段" className="select select-bordered select-sm" disabled={!!locked} value={stage} onChange={(e) => setStage(e.target.value)}>
        <option value="">阶段（可选）</option>
        {(meta.stages || []).map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
      </select>
    </div>
    {batches.error && <p className="mb-2 text-xs text-error">批次加载失败：{batches.error.message}</p>}
    <FileUploader accept=".zip" maxMb={500} label="上传 ZIP" disabled={!!locked} onFile={upload} />
    {jobId && <div className="surface-card mt-4 p-3 text-sm" role="status" aria-live="polite">
      <div className="mb-2">文件归属识别 · {JOB_STATUS[job?.status] || "获取任务状态中"}</div>
      <progress className={`progress w-full ${job?.status === "FAILED" ? "progress-error" : "progress-primary"}`} value={job?.progress ?? (ready ? 100 : 5)} max="100" />
      {job?.error && <p className="mt-2 text-xs text-error">{job.error}</p>}
      {pollingError && <p className="mt-2 text-xs text-error">任务状态获取失败，正在重试：{pollingError.message}</p>}
      {ready && !items.length && <p className="mt-2 text-xs">未识别到可导入的文件。可检查 ZIP 内容后重新上传。</p>}
    </div>}
    {items.length > 0 && <div className="surface-card mt-4 overflow-x-auto">
      <div className="space-y-2 p-3 text-xs">
        <p>共 {items.length} 个文件 · 已导入 {imported} 个 · 待处理 {pending} 个 · 失败 {failed} 个</p>
        <p className="text-base-content/60">请核对每个文件的归属与类型；匹配成功的文件也需要点击「确认导入」。导入使用所选档案的当前发展阶段。</p>
        <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); setQuery(search.trim()) }}>
          <input aria-label="搜索归属档案" className="input input-bordered input-sm" placeholder="输入姓名或学号查找档案" value={search} onChange={(e) => setSearch(e.target.value)} />
          <button type="submit" className="btn btn-outline btn-sm" disabled={archives.loading}>查找归属档案</button>
        </form>
        {archives.error && <p className="text-error">档案查询失败：{archives.error.message}</p>}
        {query && !archives.loading && !archives.error && !archives.data?.items?.length && <p>未找到匹配档案，请更换姓名或学号。</p>}
      </div>
      <table className="table table-sm">
        <thead><tr><th>文件</th><th>识别学号</th><th>归属档案</th><th>材料类型</th><th>跳过</th><th>状态</th></tr></thead>
        <tbody>{items.map((item) => {
          const draft = batchDraft(item, assigns[item.item_id])
          const done = ["IMPORTED", "SKIPPED"].includes(item.status)
          const options = new Map((archives.data?.items || []).map((archive) => [String(archive.id), archive]))
          if (item.matched_archive) options.set(String(item.matched_archive.id), item.matched_archive)
          if (assigns[item.item_id]?.archive) options.set(String(assigns[item.item_id].archive.id), assigns[item.item_id].archive)
          return <tr key={item.item_id}>
            <td className="max-w-xs break-all text-xs">{item.entry_path}</td>
            <td className="mono text-xs">{item.parsed_student_no || "—"}</td>
            <td className="text-xs">{done ? (item.matched_archive ? <Link className="link" to={`/archives/${item.matched_archive.id}`}>{item.matched_archive.real_name}</Link> : "—") :
              <select aria-label={`${item.entry_path} 的归属档案`} className="select select-bordered select-xs max-w-56" disabled={saving || draft.skip} value={draft.archive_id} onChange={(e) => updateDraft(item.item_id, { archive_id: e.target.value, archive: options.get(e.target.value) })}>
                <option value="">请选择归属档案</option>
                {[...options.values()].map((archive) => <option key={archive.id} value={archive.id}>{archive.real_name}{archive.student_no ? ` · ${archive.student_no}` : ""}</option>)}
              </select>}
            </td>
            <td className="text-xs">{done ? (item.material_type || "自动识别") :
              <select aria-label={`${item.entry_path} 的材料类型`} className="select select-bordered select-xs max-w-44" disabled={saving || draft.skip} value={draft.material_type_id} onChange={(e) => updateDraft(item.item_id, { material_type_id: e.target.value })}>
                <option value="">{item.material_type ? `识别：${item.material_type}` : "自动识别类型"}</option>
                {(meta.material_types || []).map((type) => <option key={type.id} value={type.id}>{type.name}</option>)}
              </select>}
            </td>
            <td><input aria-label={`跳过 ${item.entry_path}`} type="checkbox" className="checkbox checkbox-xs" disabled={saving || done} checked={draft.skip || item.status === "SKIPPED"} onChange={(e) => updateDraft(item.item_id, { skip: e.target.checked })} /></td>
            <td className={`text-xs ${item.status === "FAILED" ? "text-error" : ""}`}>{STATUS[item.status] || item.status}{item.error ? ` · ${item.error}` : ""}</td>
          </tr>
        })}</tbody>
      </table>
      {ready && pending > 0 && <div className="space-y-2 p-3">
        <button type="button" className="btn btn-primary btn-sm" disabled={saving || (!body.assignments.length && !body.skip_item_ids.length)} onClick={saveAssign}>
          {saving ? "正在导入…" : `确认导入 ${body.assignments.length} 个文件${body.skip_item_ids.length ? `，跳过 ${body.skip_item_ids.length} 个` : ""}`}
        </button>
        {pending > body.assignments.length + body.skip_item_ids.length && <p className="text-xs text-warning">未指定归属的文件会保留，待选择档案后再导入。</p>}
      </div>}
      {saveError && <p role="alert" className="p-3 text-xs text-error">{saveError}</p>}
    </div>}
  </div>
}
