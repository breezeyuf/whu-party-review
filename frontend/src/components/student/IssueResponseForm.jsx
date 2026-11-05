import { useEffect, useRef, useState } from "react"
import FileUploader from "../common/FileUploader"
import { uploadVersion } from "../../api/materials"
import { respondIssue } from "../../api/issues"
import StudentTaskProgress from "../../utils/student/StudentTaskProgress"
import { issueMaterialId } from "../../utils/studentWorkflow"

export default function IssueResponseForm({ issue, onDone, onBusyChange, compact = false, drafts, draftKey = issue.id }) {
  const [text, setText] = useState(() => drafts?.get(draftKey) ?? issue.response_text ?? "")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [jobId, setJobId] = useState(null)
  const [finishedJobId, setFinishedJobId] = useState(null)
  const [uploadedVersion, setUploadedVersion] = useState(null)
  const [saved, setSaved] = useState(false)
  const requestLock = useRef(false)
  const busyCallback = useRef(onBusyChange)
  const taskPending = !!jobId && String(jobId) !== String(finishedJobId)
  const working = busy || taskPending
  const materialId = issueMaterialId(issue)

  useEffect(() => { busyCallback.current = onBusyChange }, [onBusyChange])
  useEffect(() => {
    busyCallback.current?.(working)
    return () => busyCallback.current?.(false)
  }, [working])

  const saveVersionReply = async (version) => {
    await respondIssue(issue.id, { response_type: "MODIFIED", response_text: text.trim() || "已重新上传", version_id: version.id })
    drafts?.delete(draftKey)
    setSaved(true)
    onDone?.()
  }

  const explain = async () => {
    if (requestLock.current || working) return
    if (text.trim().length < 10) { setError("情况说明不少于 10 字"); return }
    requestLock.current = true
    setBusy(true)
    setError("")
    try {
      await respondIssue(issue.id, { response_type: "EXPLAINED", response_text: text.trim() })
      drafts?.delete(draftKey)
      setSaved(true)
      onDone?.()
    } catch (e) {
      setError(e.message || "提交失败")
    } finally {
      setBusy(false)
      requestLock.current = false
    }
  }

  const upload = async (file) => {
    if (requestLock.current || working) throw new Error("请等待当前整改操作完成")
    if (!materialId) throw new Error("该问题没有关联材料，请使用情况说明或先到我的材料补交")
    requestLock.current = true
    setBusy(true)
    setSaved(false)
    setError("")
    try {
      const res = await uploadVersion(materialId, file, { change_note: text.trim() || "按整改意见替换", issue_ids: String(issue.id) })
      if (!res?.version?.id) throw new Error("材料已上传，但未返回版本编号。请刷新核对，避免重复上传")
      setUploadedVersion(res.version)
      if (res.parse_job_id) {
        setFinishedJobId(null)
        setJobId(res.parse_job_id)
      }
      // Persist the explanation and the real version together. The upload API
      // links issue_ids atomically but does not save response_text.
      await saveVersionReply(res.version)
    } catch (e) {
      setError(e.message || "上传失败")
    } finally {
      setBusy(false)
      requestLock.current = false
    }
  }

  const retryReply = async () => {
    if (!uploadedVersion || requestLock.current || working) return
    requestLock.current = true
    setBusy(true)
    setError("")
    try { await saveVersionReply(uploadedVersion) }
    catch (e) { setError(e.message || "保存整改说明失败") }
    finally { setBusy(false); requestLock.current = false }
  }

  return (
    <details className="service-inline-details" open={!compact ? true : undefined}>
      <summary hidden={!compact}>{issue.response_type ? "查看或修改整改回复" : "填写整改回复"}{working ? "（处理中）" : ""}</summary>
      <div className="space-y-3 rounded bg-base-200 p-3">
      {(saved || issue.response_type) && <p className="text-xs text-success">已保存整改回复，等待复核确认。{uploadedVersion && `关联材料版本 v${uploadedVersion.version_no}`}</p>}
      <textarea className="textarea textarea-bordered textarea-xs w-full" rows={2} aria-label="整改说明" placeholder="整改说明；情况说明不少于 10 字" value={text} disabled={working} onChange={(e) => { setText(e.target.value); drafts?.set(draftKey, e.target.value); setSaved(false) }} />
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="btn btn-ghost btn-xs" disabled={working} onClick={explain}>保存情况说明</button>
        {uploadedVersion && !saved && <button type="button" className="btn btn-outline btn-xs" disabled={working} onClick={retryReply}>保存已上传版本的整改说明</button>}
      </div>
      {materialId ? <FileUploader compact accept=".pdf,.jpg,.jpeg,.png,.docx" label="重新上传" hint="上传修改后的材料，解析完成后再提交" disabled={working} onFile={upload} /> : <p className="text-xs text-base-content/60">该问题没有关联材料，可填写情况说明；缺失材料请到“我的材料”补交。</p>}
      {jobId && <StudentTaskProgress jobId={jobId} onDone={(job) => { setFinishedJobId(job.id); onDone?.() }} onRestart={() => setFinishedJobId(null)} />}
      {error && <p className="text-xs text-error">{error}</p>}
      </div>
    </details>
  )
}
