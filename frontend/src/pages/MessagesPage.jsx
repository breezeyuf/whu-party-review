import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Mail, MailOpen } from "lucide-react"
import PageHeader from "../components/layout/PageHeader"
import DataTable, { Pager } from "../components/common/DataTable"
import { Loading, ErrorState } from "../components/common/States"
import { useRequest } from "../hooks/useRequest"
import { usePagination } from "../hooks/usePagination"
import { listMessages, markAllRead, markRead } from "../api/messages"
import { fmtDateTime } from "../utils/format"
import { useAuth } from "../context/AuthContext"
import { useToast } from "../context/ToastContext"

export default function MessagesPage() {
  const { query, setPage } = usePagination()
  const nav = useNavigate()
  const { activeRole } = useAuth()
  const toast = useToast()
  const isStudent = activeRole?.role === "STUDENT"
  const [filter, setFilter] = useState("")
  const [markingAll, setMarkingAll] = useState(false)
  const { data, loading, error, reload } = useRequest(
    () => listMessages({ ...query, is_read: filter === "" ? undefined : filter }),
    [query.page, query.page_size, filter],
  )

  // 后端 link_type 为小写（submission/notice/archive/job/material），且学生与审核端的落地页不同
  const navTarget = (row) => {
    const t = String(row.link_type || "").toLowerCase()
    const id = row.link_id
    if (!t || !id) return null
    if (t === "submission") return isStudent ? "/my/progress" : `/review/submissions/${id}`
    if (t === "notice") return isStudent ? "/my/rectification" : "/notices"
    if (t === "archive") return isStudent ? "/my/progress" : `/archives/${id}`
    if (t === "material") return `/materials/${id}`
    if (t === "job") return isStudent ? null : "/tasks/jobs"
    return null
  }

  const open = async (row) => {
    if (!row.is_read) {
      try {
        await markRead(row.id)
      } catch (error) {
        toast.error(error.message || "标记已读失败，未读提示暂时保留")
      }
    }
    const to = navTarget(row)
    if (to) nav(to)
    else await reload().catch(() => {})
  }

  const readAll = async () => {
    setMarkingAll(true)
    try {
      await markAllRead()
      toast.success("全部消息已读")
      await reload().catch(() => toast.info("消息已标记为已读，但列表刷新失败；请重新加载页面"))
    } catch (error) {
      toast.error(error.message || "操作失败，请重试")
    } finally {
      setMarkingAll(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="消息中心"
        extra={(
          <button type="button" className="btn btn-ghost btn-sm" disabled={markingAll} onClick={readAll}>
            {markingAll ? <span className="loading loading-spinner loading-xs" /> : <MailOpen size={16} strokeWidth={1.8} />}
            全部已读
          </button>
        )}
      />
      <div className="mb-3 flex gap-2">
        {[["", "全部"], ["false", "未读"], ["true", "已读"]].map(([v, label]) => (
          <button key={label} type="button" className={`btn btn-xs ${filter === v ? "btn-primary" : "btn-ghost"}`} onClick={() => setFilter(v)}>{label}</button>
        ))}
      </div>
      {error && <ErrorState error={error} onRetry={reload} />}
      {loading && !data ? <Loading /> : (
        <div className="surface-card p-2">
          <DataTable
            columns={[
              { key: "title", title: "标题", render: (r) => (
                <button type="button" className={`flex items-center gap-2 text-left ${r.is_read ? "text-base-content/60" : "font-medium"}`} onClick={() => open(r)}>
                  {r.is_read ? <MailOpen size={15} strokeWidth={1.8} aria-label="已读" /> : <Mail size={15} strokeWidth={1.8} aria-label="未读" />}
                  <span>{r.title}</span>
                  {!r.is_read && <span className="badge badge-primary badge-xs">未读</span>}
                </button>
              ) },
              { key: "content", title: "内容", render: (r) => <span className="line-clamp-2 text-xs text-base-content/70">{r.content}</span> },
              { key: "time", title: "时间", render: (r) => <span className="mono text-xs">{fmtDateTime(r.created_at)}</span> },
            ]}
            rows={data?.items || []}
            empty="没有消息"
          />
          <div className="px-2 pb-2"><Pager page={data?.page} pageSize={data?.page_size} total={data?.total} onPage={setPage} /></div>
        </div>
      )}
    </div>
  )
}
