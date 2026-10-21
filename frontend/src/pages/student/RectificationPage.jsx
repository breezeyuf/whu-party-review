import { useState } from "react"
import { RotateCcw } from "lucide-react"
import PageHeader from "../../components/layout/PageHeader"
import IssueList from "../../components/review/IssueList"
import IssueResponseForm from "../../components/student/IssueResponseForm"
import RecheckSummary from "../../components/review/RecheckSummary"
import NoticePreview from "../../components/notice/NoticePreview"
import { Loading, ErrorState } from "../../components/common/States"
import { useRequest } from "../../hooks/useRequest"
import { myArchive } from "../../api/archives"
import { listIssues } from "../../api/issues"
import { getNotice, listNotices } from "../../api/notices"
import { getReport } from "../../api/reports"
import { getSubmission, submitSubmission } from "../../api/submissions"
import { useToast } from "../../context/ToastContext"
import { StatusBadge } from "../../components/common/Badges"

export default function RectificationPage() {
  const toast = useToast()
  const archiveReq = useRequest(() => myArchive(), [])
  const archive = archiveReq.data
  const subId = archive?.current_submission?.id
  const subReq = useRequest(() => (subId ? getSubmission(subId) : null), [subId], { immediate: !!subId })
  const issueReq = useRequest(() => (subId ? listIssues(subId) : { items: [] }), [subId], { immediate: !!subId })
  const noticeReq = useRequest(() => listNotices({ submission_id: subId, page_size: 5 }), [subId], { immediate: !!subId })
  const [notice, setNotice] = useState(null)
  const [loadingNoticeId, setLoadingNoticeId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  const reportId = subReq.data?.latest_report?.id
  const reportReq = useRequest(() => (reportId ? getReport(reportId) : null), [reportId], { immediate: !!reportId })

  const openNotice = async (id) => {
    setLoadingNoticeId(id)
    try {
      setNotice(await getNotice(id))
    } catch (error) {
      toast.error(error.message || "通知加载失败")
    } finally {
      setLoadingNoticeId(null)
    }
  }

  const resubmit = async () => {
    setBusy(true)
    setError("")
    try {
      await submitSubmission(subId, {})
      toast.success("已重新提交，系统将自动复核")
      setError("")
      await Promise.all([subReq.reload(), issueReq.reload()]).catch(() => {
        toast.info("重新提交已成功，但页面状态刷新失败；请重新加载页面")
      })
    } catch (e) {
      setError(e.message || "还不能重新提交")
    } finally {
      setBusy(false)
    }
  }

  if (archiveReq.loading && !archive) return <Loading />
  if (archiveReq.error) return <ErrorState error={archiveReq.error} onRetry={archiveReq.reload} />
  if (!subId) {
    return (
      <div>
        <PageHeader title="整改中心" />
        <p className="text-sm text-base-content/60">当前没有待整改的提交。</p>
      </div>
    )
  }

  const returned = subReq.data?.status === "RETURNED" || subReq.data?.status === "DRAFT"
  if (subReq.loading && !subReq.data) return <Loading />
  if (subReq.error) return <ErrorState error={subReq.error} onRetry={subReq.reload} />

  return (
    <div>
      <PageHeader
        title="整改中心"
        extra={(
          <div className="flex items-center gap-2">
            <StatusBadge code={subReq.data?.status} />
            <button type="button" className="btn btn-primary btn-sm" disabled={busy || !returned} onClick={resubmit}>
              <RotateCcw size={15} strokeWidth={1.8} />
              {busy ? "提交中…" : "重新提交"}
            </button>
          </div>
        )}
      >
        逐条回复已确认的问题。全部处理后再提交，系统会自动复核。
      </PageHeader>
      {error && <div className="alert alert-error mb-3 text-sm">{error}</div>}
      {reportReq.data?.recheck_summary && (
        <div className="mb-4"><RecheckSummary summary={reportReq.data.recheck_summary} /></div>
      )}
      <div className="grid gap-4 lg:grid-cols-5">
        <section className="lg:col-span-3">
          {issueReq.loading && !issueReq.data ? <Loading /> : issueReq.error ? <ErrorState error={issueReq.error} onRetry={issueReq.reload} /> : (
            <IssueList
              issues={issueReq.data?.items || []}
              renderFooter={(issue) => returned ? <IssueResponseForm issue={issue} onDone={() => issueReq.reload().catch(() => {})} /> : null}
            />
          )}
        </section>
        <aside className="lg:col-span-2 space-y-3">
          <h2 className="text-sm font-medium">整改通知</h2>
          {noticeReq.error && <div className="alert alert-error text-xs">通知加载失败：{noticeReq.error.message}<button type="button" className="btn btn-xs" onClick={noticeReq.reload}>重试</button></div>}
          {noticeReq.loading && !noticeReq.data && <p className="text-xs text-base-content/50">正在加载通知…</p>}
          <ul className="space-y-2">
            {(noticeReq.data?.items || []).map((n) => (
              <li key={n.id}>
                <button type="button" className="btn btn-ghost btn-sm h-auto w-full justify-start py-2 text-left" disabled={loadingNoticeId === n.id} onClick={() => openNotice(n.id)}>
                  <span>
                    <span className="block">{loadingNoticeId === n.id ? "正在打开…" : n.title}</span>
                    <span className="text-xs text-base-content/50">{n.item_count} 条 · {n.status}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
          <NoticePreview notice={notice} />
        </aside>
      </div>
    </div>
  )
}
