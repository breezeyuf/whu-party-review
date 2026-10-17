import { useState } from "react"
import FileUploader from "../common/FileUploader"
import { uploadVersion } from "../../api/materials"
import { respondIssue } from "../../api/issues"

export default function IssueResponseForm({ issue, onDone }) {
  const [text, setText] = useState(issue.response_text || "")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  const explain = async () => {
    if (text.trim().length < 10) { setError("情况说明不少于 10 字"); return }
    setBusy(true)
    setError("")
    try {
      await respondIssue(issue.id, { response_type: "EXPLAINED", response_text: text.trim() })
      onDone?.()
    } catch (e) {
      setError(e.message || "提交失败")
    } finally {
      setBusy(false)
    }
  }

  const upload = async (file) => {
    if (!issue.material_id && !issue.location?.material_id) {
      setError("该问题没有关联材料，请使用情况说明")
      return
    }
    const mid = issue.material_id || issue.location.material_id
    setBusy(true)
    setError("")
    try {
      const res = await uploadVersion(mid, file, { change_note: text || "按整改意见替换", issue_ids: String(issue.id) })
      if (!res?.responded_issue_ids?.includes?.(issue.id)) {
        await respondIssue(issue.id, { response_type: "MODIFIED", response_text: text || "已重新上传", version_id: res?.version?.id })
      }
      onDone?.()
    } catch (e) {
      setError(e.message || "上传失败")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-2 rounded bg-base-200 p-2">
      <textarea className="textarea textarea-bordered textarea-xs w-full" rows={2} placeholder="整改说明" value={text} onChange={(e) => setText(e.target.value)} />
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="btn btn-ghost btn-xs" disabled={busy} onClick={explain}>情况说明</button>
      </div>
      <FileUploader accept=".pdf,.jpg,.jpeg,.png,.docx" label="重新上传" hint="上传新版本，记为已修改" disabled={busy} onFile={upload} />
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  )
}
