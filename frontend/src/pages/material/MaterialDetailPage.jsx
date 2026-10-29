import { useEffect, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import PageHeader from "../../components/layout/PageHeader"
import MaterialViewer from "../../components/material/MaterialViewer"
import ParsedTextPanel from "../../components/material/ParsedTextPanel"
import VersionList from "../../components/material/VersionList"
import VersionDiff from "../../components/material/VersionDiff"
import TypeConfirmSelect from "../../components/material/TypeConfirmSelect"
import FileUploader from "../../components/common/FileUploader"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { useJobPolling } from "../../hooks/useJobPolling"
import { getDiff, getMaterial, getParsed, listVersions, putParsed, setType, uploadVersion, retryParse } from "../../api/materials"
import { listIssues } from "../../api/issues"
import { getSubmission } from "../../api/submissions"
import IssueList from "../../components/review/IssueList"
import { fmtSize } from "../../utils/format"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import { isReviewer, isStudent } from "../../utils/permissions"
import { materialFocus, PARSE_PENDING, positiveInteger } from "../../utils/materialWorkflow"

export default function MaterialDetailPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const queryKey = searchParams.toString()
  const toast = useToast()
  const { activeRole } = useAuth()
  const mat = useRequest(() => getMaterial(id), [id])
  const versions = useRequest(() => listVersions(id), [id])
  const [tab, setTab] = useState("preview")
  const [versionId, setVersionId] = useState(null)
  const [page, setPage] = useState(1)
  const [activeIssueId, setActiveIssueId] = useState(null)
  const [sourceBox, setSourceBox] = useState(null)
  const [diff, setDiff] = useState(null)
  const [diffFrom, setDiffFrom] = useState("")
  const [diffTo, setDiffTo] = useState("")
  const [diffLoading, setDiffLoading] = useState(false)
  const [diffError, setDiffError] = useState("")
  const [taskId, setTaskId] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [refreshError, setRefreshError] = useState("")
  const [uploading, setUploading] = useState(false)
  const [reparsing, setReparsing] = useState(false)
  const initialized = useRef("")
  const diffRequest = useRef(0)
  const m = mat.data
  const vid = versionId || m?.current_version?.id
  const parsed = useRequest(() => getParsed(id, { version_id: vid }), [id, vid], { immediate: !!vid })
  const subId = m?.submission_id
  const issues = useRequest(() => listIssues(subId, { material_id: id }), [subId, id], { immediate: !!subId })
  const submission = useRequest(() => getSubmission(subId), [subId, activeRole?.role, activeRole?.org_id], { immediate: !!subId })
  const reviewer = isReviewer(activeRole)
  const student = isStudent(activeRole)
  const allVersions = versions.data || []
  const selectedVersion = allVersions.find((version) => String(version.id) === String(vid)) || (String(m?.current_version?.id) === String(vid) ? m?.current_version : null)
  const historical = !!vid && String(vid) !== String(m?.current_version?.id)
  const activeIssue = (issues.data?.items || []).find((issue) => String(issue.id) === String(activeIssueId))
  const canUpload = !!submission.data?.can?.upload
  const canCorrect = reviewer && (canUpload || !!submission.data?.can?.review)
  const comparisonReady = [diffFrom, diffTo].every((value) => allVersions.some((version) => String(version.id) === value && version.parse_status === "DONE"))

  const refresh = async () => {
    const results = await Promise.allSettled([mat.reload(), versions.reload(), parsed.reload(), issues.reload(), submission.reload()])
    setRefreshKey((key) => key + 1)
    const failure = results.find((result) => result.status === "rejected")
    setRefreshError(failure ? failure.reason?.message || "部分数据刷新失败，请重试" : "")
  }

  const { job, error: jobError } = useJobPolling(taskId, {
    onDone: (completed) => {
      refresh()
      if (["FAILED", "PARTIAL", "CANCELLED"].includes(completed.status)) toast.error(completed.error || "处理未成功，请查看任务提示")
      else toast.success(completed.job_type === "PARSE" ? "材料解析完成" : "重新校验完成")
    },
  })

  useEffect(() => {
    initialized.current = ""
    diffRequest.current += 1
    setTab("preview"); setVersionId(null); setPage(1); setActiveIssueId(null); setSourceBox(null)
    setTaskId(null); setDiff(null); setDiffFrom(""); setDiffTo(""); setDiffError(""); setDiffLoading(false); setRefreshError("")
  }, [id])

  useEffect(() => {
    initialized.current = ""
    setTab("preview"); setVersionId(null); setPage(1); setActiveIssueId(null); setSourceBox(null)
  }, [queryKey])

  useEffect(() => {
    if (!m || String(m.id) !== String(id) || !versions.data) return
    if (m.current_version && !versions.data.some((version) => String(version.id) === String(m.current_version.id))) return
    const key = `${id}?${queryKey}`
    if (initialized.current === key) return
    const issueId = positiveInteger(searchParams.get("issue_id"))
    if (issueId && !issues.data && !issues.error) return
    const issue = (issues.data?.items || []).find((item) => String(item.id) === String(issueId))
    const focus = materialFocus({ issue, searchParams, versions: versions.data, currentVersion: m.current_version })
    setVersionId(focus.versionId)
    setPage(focus.page)
    setActiveIssueId(issue?.id || null)
    setSourceBox(!issue && focus.bbox ? { id: "source", page_no: focus.page, bbox: focus.bbox, title: "时间节点来源" } : null)
    if (issueId && !issue) setRefreshError("未找到该问题，可能已更新或当前角色无权查看。")
    initialized.current = key
  }, [id, queryKey, m, versions.data, issues.data, issues.error, searchParams])

  useEffect(() => {
    if (!allVersions.length || String(m?.id) !== String(id)) return
    setDiffFrom((value) => allVersions.some((version) => String(version.id) === value) ? value : String(allVersions[Math.max(0, allVersions.length - 2)].id))
    setDiffTo((value) => allVersions.some((version) => String(version.id) === value) ? value : String(allVersions[allVersions.length - 1].id))
  }, [versions.data, id, m?.id])

  // Also follow a parse that started on the upload page before this page opened.
  useEffect(() => {
    if (!m || !PARSE_PENDING.has(m.current_version?.parse_status)) return
    let alive = true
    let timer
    const poll = async () => {
      try {
        const fresh = await getMaterial(id)
        if (!alive) return
        setRefreshError("")
        if (!PARSE_PENDING.has(fresh.current_version?.parse_status)) {
          setRefreshKey((key) => key + 1)
          mat.setData(fresh)
          await Promise.allSettled([versions.reload(), parsed.reload(), issues.reload()])
          return
        }
        mat.setData(fresh)
      } catch (error) { if (alive) setRefreshError(`解析状态获取失败，正在重试：${error.message}`) }
      if (alive) timer = setTimeout(poll, 1800)
    }
    timer = setTimeout(poll, 1800)
    return () => { alive = false; clearTimeout(timer) }
  }, [id, m?.current_version?.parse_status, mat.setData, versions.reload, parsed.reload, issues.reload])

  const selectIssue = (issue) => {
    const focus = materialFocus({ issue, versions: allVersions, currentVersion: m.current_version })
    setActiveIssueId(issue.id); setVersionId(focus.versionId); setPage(focus.page); setSourceBox(null); setTab("preview")
  }

  const selectVersion = (version) => {
    setVersionId(version.id); setPage(1); setActiveIssueId(null); setSourceBox(null); setTab("preview")
  }

  const compare = async () => {
    if (!diffFrom || !diffTo || diffFrom === diffTo || !comparisonReady) return
    const request = ++diffRequest.current
    setDiffLoading(true); setDiffError(""); setDiff(null)
    try {
      const result = await getDiff(id, { from_version: Number(diffFrom), to_version: Number(diffTo) })
      if (request === diffRequest.current) setDiff(result)
    } catch (error) { if (request === diffRequest.current) setDiffError(error.message || "版本对比失败") }
    finally { if (request === diffRequest.current) setDiffLoading(false) }
  }

  if (mat.loading && !m) return <Loading />
  if (mat.error) return <ErrorState error={mat.error} onRetry={mat.reload} />
  if (!m) return null

  const highlights = (issues.data?.items || [])
    .filter((issue) => !issue.material_version_id && !issue.location?.version_id ? !historical : String(issue.material_version_id || issue.location.version_id) === String(vid))
    .map((issue) => ({ id: issue.id, page_no: issue.location?.page_no, bbox: issue.location?.bbox, title: issue.title }))
  if (sourceBox) highlights.push(sourceBox)

  return <div>
    <PageHeader title={m.title || m.type?.name || "材料"} crumbs={[{ label: student ? "我的材料" : "档案", to: student ? "/my/materials" : `/archives/${m.archive_id}` }, { label: "材料" }]}>
      {m.type?.name || "类型未确认"} · {m.type_status} · 置信度 {m.type_confidence ?? "—"} · 第 {selectedVersion?.version_no || "—"} 版 · {fmtSize(selectedVersion?.file_size)} · {selectedVersion?.page_count || 0} 页
    </PageHeader>
    {historical && <div className="alert alert-info mb-3 py-2 text-xs">当前查看历史版本，仅供阅读与对比。<button type="button" className="btn btn-ghost btn-xs" onClick={() => selectVersion(m.current_version)}>返回当前版本</button></div>}
    <div className="mb-4"><TypeConfirmSelect value={m.type?.id} disabled={historical || (!canUpload && !canCorrect)} onConfirm={async (typeId) => { const updated = await setType(id, typeId); mat.setData(updated); toast.success("类型已确认") }} /></div>
    {submission.error && <p role="alert" className="mb-2 text-xs text-error">材料操作权限加载失败：{submission.error.message} <button type="button" className="link" onClick={() => submission.reload().catch(() => {})}>重试</button></p>}
    {PARSE_PENDING.has(m.current_version?.parse_status) && <p role="status" className="mb-3 text-xs text-info">当前版本正在解析，完成后会自动刷新预览和解析文本。</p>}
    {selectedVersion?.parse_status === "FAILED" && <div role="alert" className="alert alert-error mb-3 py-2 text-xs">材料解析失败：{selectedVersion.parse_error || "请检查文件是否完整，并重新上传。"}</div>}
    {canUpload && !historical && !selectedVersion?.is_frozen && <button type="button" className="btn btn-outline btn-sm mb-3" disabled={reparsing || PARSE_PENDING.has(selectedVersion?.parse_status)} onClick={async () => {
      setReparsing(true)
      try { const result = await retryParse(id); setTaskId(result.parse_job_id); await refresh(); toast.success("已安排重新解析，保留人工校正") }
      catch (e) { toast.error(e.message || "重新解析失败") }
      finally { setReparsing(false) }
    }}>{selectedVersion?.parse_status === "FAILED" ? "重试解析" : "重新解析（使用当前模型配置）"}</button>}
    {taskId && Number(job?.id) === Number(taskId) && <div role="status" aria-live="polite" className="surface-card mb-3 p-3 text-xs">
      <p>{job.stage_text || "材料处理任务"} · {({ QUEUED: "排队中", RUNNING: "处理中", SUCCEEDED: "已完成", FAILED: "失败", PARTIAL: "部分失败", CANCELLED: "已取消" })[job.status] || job.status}</p>
      <progress className="progress progress-primary mt-2 w-full" value={job.progress ?? 0} max="100" />
      {job.error && <p className="mt-1 text-error">{job.error}</p>}
    </div>}
    {jobError && <p role="alert" className="mb-2 text-xs text-error">任务状态获取失败，正在重试：{jobError.message}</p>}
    {refreshError && <p role="alert" className="mb-2 text-xs text-error">{refreshError} <button type="button" className="link" onClick={refresh}>刷新</button></p>}
    {versions.error && <p role="alert" className="mb-2 text-xs text-error">版本列表加载失败，来源定位可能不完整。<button type="button" className="link" onClick={() => versions.reload().catch(() => {})}>重试</button></p>}
    <div role="tablist" className="tabs tabs-bordered mb-3">
      {[["preview", "预览"], ["text", "解析文本"], ["versions", "版本"], ["issues", "问题"]].map(([key, label]) => <button key={key} type="button" role="tab" aria-selected={tab === key} className={`tab ${tab === key ? "tab-active" : ""}`} onClick={() => setTab(key)}>{label}</button>)}
    </div>
    {tab === "preview" && <>
      {activeIssue && <div className="surface-card mb-3 p-3 text-xs"><p className="font-medium">问题定位：{activeIssue.title}</p><p className="mt-1">{activeIssue.description}</p>{!activeIssue.location?.bbox && <p className="mt-1 text-base-content/60">该问题未提供框选坐标，请结合问题描述核查页面。</p>}</div>}
      <MaterialViewer materialId={m.id} versionId={vid} page={page} onPage={setPage} pageCount={selectedVersion?.page_count} highlights={highlights} activeId={activeIssueId || (sourceBox ? "source" : null)} refreshKey={refreshKey} />
    </>}
    {tab === "text" && <div className="surface-card p-4">
      {parsed.loading || (parsed.data && String(parsed.data.version_id) !== String(vid)) ? <Loading label="解析文本" /> : parsed.error ? <ErrorState error={parsed.error} onRetry={parsed.reload} /> :
        <ParsedTextPanel parsed={parsed.data} editable={canCorrect && !historical && selectedVersion?.parse_status === "DONE"} onSave={async (body) => {
          const result = await putParsed(id, body)
          toast.success(body.recheck ? "已保存校正，正在重新校验" : "已保存校正")
          if (result.job_id) setTaskId(result.job_id)
          await parsed.reload()
        }} />}
    </div>}
    {tab === "versions" && <div className="grid gap-4 lg:grid-cols-2">
      <div>
        {versions.error ? <ErrorState error={versions.error} onRetry={versions.reload} /> : <VersionList versions={allVersions} currentId={vid} onSelect={selectVersion}
          reportHref={subId ? (rid) => `${student ? `/my/self-check/${subId}` : `/review/submissions/${subId}`}?report=${rid}` : undefined} />}
        {canUpload && <div className="mt-3"><FileUploader accept=".pdf,.jpg,.jpeg,.png,.docx" disabled={uploading} label="上传新版本" onFile={async (file) => {
          setUploading(true)
          try {
            const result = await uploadVersion(id, file, { change_note: "替换材料" })
            setVersionId(result.version.id); setPage(1); setActiveIssueId(null); setSourceBox(null)
            setTaskId(result.parse_job_id); setDiff(null)
            await Promise.allSettled([versions.reload(), mat.reload()])
            toast.success("新版本已上传，正在解析")
          } finally { setUploading(false) }
        }} /></div>}
        {allVersions.length >= 2 ? <div className="mt-3 flex flex-wrap items-center gap-2">
          <select aria-label="对比起始版本" className="select select-bordered select-sm" disabled={diffLoading} value={diffFrom} onChange={(e) => { setDiffFrom(e.target.value); setDiff(null); setDiffError("") }}>{allVersions.map((version) => <option key={version.id} value={version.id}>第 {version.version_no} 版</option>)}</select>
          <span className="text-xs">与</span>
          <select aria-label="对比目标版本" className="select select-bordered select-sm" disabled={diffLoading} value={diffTo} onChange={(e) => { setDiffTo(e.target.value); setDiff(null); setDiffError("") }}>{allVersions.map((version) => <option key={version.id} value={version.id}>第 {version.version_no} 版</option>)}</select>
          <button type="button" className="btn btn-outline btn-sm" disabled={diffLoading || !diffFrom || !diffTo || diffFrom === diffTo || !comparisonReady} onClick={compare}>{diffLoading ? "对比中…" : "对比所选版本"}</button>
          {diffFrom === diffTo && <p className="w-full text-xs text-warning">请选择两个不同版本。</p>}
          {!comparisonReady && <p className="w-full text-xs text-warning">所选版本完成解析后才能对比，解析失败的版本请先重新上传。</p>}
        </div> : <p className="mt-3 text-xs text-base-content/55">至少上传两个版本后可对比差异。</p>}
      </div>
      <div>{diffError && <p role="alert" className="mb-2 text-xs text-error">{diffError}</p>}<VersionDiff diff={diff} /></div>
    </div>}
    {tab === "issues" && (issues.loading ? <Loading label="材料问题" /> : issues.error ? <ErrorState error={issues.error} onRetry={issues.reload} /> : <IssueList issues={issues.data?.items || []} activeId={activeIssueId} onSelect={selectIssue} />)}
    {m.submission_id && reviewer && <Link className="btn btn-ghost btn-sm mt-4" to={`/review/submissions/${m.submission_id}`}>打开审核工作区</Link>}
  </div>
}
