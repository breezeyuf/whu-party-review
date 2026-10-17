import { useState } from "react"
import { Link, useParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import MaterialViewer from "../../components/material/MaterialViewer"
import ParsedTextPanel from "../../components/material/ParsedTextPanel"
import VersionList from "../../components/material/VersionList"
import VersionDiff from "../../components/material/VersionDiff"
import TypeConfirmSelect from "../../components/material/TypeConfirmSelect"
import FileUploader from "../../components/common/FileUploader"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { getDiff, getMaterial, getParsed, listVersions, putParsed, setType, uploadVersion } from "../../api/materials"
import { listIssues } from "../../api/issues"
import IssueList from "../../components/review/IssueList"
import { fmtSize } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { isStudent } from "../../utils/permissions"

export default function MaterialDetailPage() {
  const { id } = useParams()
  const toast = useToast()
  const { activeRole } = useAuth()
  const mat = useRequest(() => getMaterial(id), [id])
  const parsed = useRequest(() => getParsed(id), [id])
  const versions = useRequest(() => listVersions(id), [id])
  const [tab, setTab] = useState("preview")
  const [versionId, setVersionId] = useState(null)
  const [diff, setDiff] = useState(null)
  const m = mat.data
  const subId = m?.submission_id
  const issues = useRequest(() => (subId ? listIssues(subId, { material_id: id }) : { items: [] }), [subId, id], { immediate: !!subId })
  const reviewer = activeRole && !isStudent(activeRole)

  if (mat.loading && !m) return <Loading />
  if (mat.error) return <ErrorState error={mat.error} onRetry={mat.reload} />
  if (!m) return null

  const vid = versionId || m.current_version?.id

  return (
    <div>
      <PageHeader
        title={m.title || m.type?.name || "材料"}
        crumbs={[{ label: "档案", to: m.archive_id ? `/archives/${m.archive_id}` : "/archives" }, { label: "材料" }]}
      >
        {m.type?.name || "类型未确认"} · {m.type_status} · 置信度 {m.type_confidence ?? "—"} · {fmtSize(m.current_version?.file_size)} · {m.current_version?.page_count || 0} 页
      </PageHeader>
      <div className="mb-4">
        <TypeConfirmSelect
          value={m.type?.id}
          disabled={!m.editable && !reviewer}
          onConfirm={async (typeId) => { await setType(id, typeId); toast.success("类型已确认"); mat.reload() }}
        />
      </div>
      <div role="tablist" className="tabs tabs-bordered mb-3">
        {[["preview", "预览"], ["text", "解析文本"], ["versions", "版本"], ["issues", "问题"]].map(([k, label]) => (
          <button key={k} type="button" className={`tab ${tab === k ? "tab-active" : ""}`} onClick={() => setTab(k)}>{label}</button>
        ))}
      </div>
      {tab === "preview" && <MaterialViewer materialId={m.id} versionId={vid} highlights={(issues.data?.items || []).map((i) => ({ id: i.id, page_no: i.location?.page_no, bbox: i.location?.bbox, title: i.title }))} />}
      {tab === "text" && (
        <div className="surface-card p-4">
          <ParsedTextPanel
            parsed={parsed.data}
            editable={reviewer}
            onSave={async (body) => { await putParsed(id, body); toast.success(body.recheck ? "已保存并重新校验" : "已保存校正"); parsed.reload() }}
          />
        </div>
      )}
      {tab === "versions" && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div>
            <VersionList versions={versions.data || []} currentId={vid} onSelect={(v) => setVersionId(v.id)} />
            {m.editable && (
              <div className="mt-3">
                <FileUploader accept=".pdf,.jpg,.jpeg,.png,.docx" label="上传新版本" onFile={async (file) => {
                  await uploadVersion(id, file, { change_note: "替换材料" })
                  toast.success("新版本已上传")
                  versions.reload(); mat.reload()
                }} />
              </div>
            )}
            <button type="button" className="btn btn-ghost btn-xs mt-2" onClick={async () => {
              try {
                const params = versionId ? { from_version: undefined, to_version: versionId } : {}
                setDiff(await getDiff(id, params))
              } catch (e) {
                toast.error(e.message || "对比失败")
              }
            }}>对比最近两版</button>
          </div>
          <VersionDiff diff={diff} />
        </div>
      )}
      {tab === "issues" && <IssueList issues={issues.data?.items || []} onSelect={(issue) => setTab("preview")} />}
      {m.submission_id && <Link className="btn btn-ghost btn-sm mt-4" to={`/review/submissions/${m.submission_id}`}>打开审核工作区</Link>}
    </div>
  )
}
