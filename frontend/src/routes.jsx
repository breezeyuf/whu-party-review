import { Navigate, Outlet, useLocation } from "react-router-dom"
import { Suspense, useEffect } from "react"
import { useAuth } from "./context/AuthContext"
import { tokenStore } from "./api/client"
import { LazyShell, preloadShell, shellPage } from "./components/layout/lazyShell"
import { Loading } from "./components/common/States"
import RouteError from "./components/common/RouteError"
import { ForbiddenPage, NotFoundPage } from "./pages/StatusPages"
import { can } from "./utils/permissions"
import { identityFor, loginDestination } from "./utils/identity"
import { lazyWithRetry } from "./utils/lazyLoad"

const LoginPage = lazyWithRetry(() => import("./pages/LoginPage"))
const ChooseIdentityPage = lazyWithRetry(() => import("./pages/ChooseIdentityPage"))
const ChangePasswordPage = lazyWithRetry(() => import("./pages/ChangePasswordPage"))
// 外壳内的页面经外壳块里的导入清单加载，见 components/layout/shellModule.js
const DashboardPage = shellPage("DashboardPage")
const MessagesPage = shellPage("MessagesPage")
const ProfilePage = shellPage("ProfilePage")
const MyProgressPage = shellPage("MyProgressPage")
const MyMaterialsPage = shellPage("MyMaterialsPage")
const SelfCheckPage = shellPage("SelfCheckPage")
const RectificationPage = shellPage("RectificationPage")
const ReviewTasksPage = shellPage("ReviewTasksPage")
const ReviewWorkspacePage = shellPage("ReviewWorkspacePage")
const CrossReviewConfigPage = shellPage("CrossReviewConfigPage")
const JobsPage = shellPage("JobsPage")
const ArchiveListPage = shellPage("ArchiveListPage")
const ArchiveDetailPage = shellPage("ArchiveDetailPage")
const BatchUploadPage = shellPage("BatchUploadPage")
const MaterialDetailPage = shellPage("MaterialDetailPage")
const NoticesPage = shellPage("NoticesPage")
const ChecklistsPage = shellPage("ChecklistsPage")
const MaterialTypesPage = shellPage("MaterialTypesPage")
const TimeRulesPage = shellPage("TimeRulesPage")
const CheckRulesPage = shellPage("CheckRulesPage")
const TermsPage = shellPage("TermsPage")
const SensitivePhrasesPage = shellPage("SensitivePhrasesPage")
const SuggestionTemplatesPage = shellPage("SuggestionTemplatesPage")
const RuleVersionsPage = shellPage("RuleVersionsPage")
const StatsOverviewPage = shellPage("StatsOverviewPage")
const AiQualityPage = shellPage("AiQualityPage")
const ExportPage = shellPage("ExportPage")
const BatchesPage = shellPage("BatchesPage")
const OrgsPage = shellPage("OrgsPage")
const UsersPage = shellPage("UsersPage")
const SettingsPage = shellPage("SettingsPage")
const AuditLogsPage = shellPage("AuditLogsPage")

function Gate({ children }) {
  return <Suspense fallback={<Loading />}>{children}</Suspense>
}

function RequireAuth() {
  const { user, ready } = useAuth()
  const loc = useLocation()
  // 已有会话正在校验身份时，同时下载登录后的外壳
  useEffect(() => { if (!ready && tokenStore.access) preloadShell() }, [ready])
  if (!ready) return <Loading />
  if (!user) return <Navigate to="/login" replace state={{ from: loc.pathname }} />
  if (user.must_change_password && loc.pathname !== "/change-password") {
    return <Navigate to="/change-password" replace />
  }
  return <Outlet />
}

function RequireRole({ allow }) {
  const { activeRole } = useAuth()
  if (!can(activeRole, allow)) return <Navigate to="/403" replace />
  return <Outlet />
}

function RequireIdentity({ kind }) {
  const { user, activeRole, needsIdentitySelection } = useAuth()
  if (needsIdentitySelection || !identityFor(activeRole)) return <Navigate to="/choose-identity" replace />
  if (kind && identityFor(activeRole).kind !== kind) return <Navigate to={loginDestination(user)} replace />
  return <Outlet />
}

function IdentityHome() {
  const { user } = useAuth()
  return <Navigate to={loginDestination(user)} replace />
}

const page = (el) => ({ element: el })

// 登录后在外壳内显示的页面
const shellPages = [
  { path: "/", ...page(<IdentityHome />) },
  { element: <RequireIdentity kind="student" />, children: [{ path: "/student", ...page(<DashboardPage />) }] },
  { element: <RequireIdentity kind="reviewer" />, children: [{ path: "/review", ...page(<DashboardPage />) }] },
  { element: <RequireIdentity kind="admin" />, children: [{ path: "/admin", ...page(<DashboardPage />) }] },
  { path: "/messages", ...page(<MessagesPage />) },
  { path: "/profile", ...page(<ProfilePage />) },
  { path: "/403", ...page(<ForbiddenPage />) },
  {
    element: <RequireRole allow="student" />,
    children: [
      { path: "/my/progress", ...page(<MyProgressPage />) },
      { path: "/my/materials", ...page(<MyMaterialsPage />) },
      { path: "/my/self-check/:submissionId", ...page(<SelfCheckPage />) },
      { path: "/my/rectification", ...page(<RectificationPage />) },
    ],
  },
  { element: <RequireRole allow="materialRead" />, children: [{ path: "/materials/:id", ...page(<MaterialDetailPage />) }] },
  {
    element: <RequireRole allow="review" />,
    children: [
      { path: "/review/tasks", ...page(<ReviewTasksPage />) },
      { path: "/review/submissions/:id", ...page(<ReviewWorkspacePage />) },
    ],
  },
  {
    element: <RequireRole allow="archives" />,
    children: [
      { path: "/archives", ...page(<ArchiveListPage />) },
      { path: "/archives/:id", ...page(<ArchiveDetailPage />) },
    ],
  },
  {
    element: <RequireRole allow="batchUpload" />,
    children: [{ path: "/materials/batch-upload", ...page(<BatchUploadPage />) }],
  },
  {
    element: <RequireRole allow="notices" />,
    children: [{ path: "/notices", ...page(<NoticesPage />) }],
  },
  {
    element: <RequireRole allow="cross" />,
    children: [{ path: "/cross-review", ...page(<CrossReviewConfigPage />) }],
  },
  {
    element: <RequireRole allow="jobs" />,
    children: [{ path: "/tasks/jobs", ...page(<JobsPage />) }],
  },
  {
    element: <RequireRole allow="rulesRead" />,
    children: [
      { path: "/rules/checklists", ...page(<ChecklistsPage />) },
      { path: "/rules/material-types", ...page(<MaterialTypesPage />) },
      { path: "/rules/time-rules", ...page(<TimeRulesPage />) },
      { path: "/rules/check-rules", ...page(<CheckRulesPage />) },
      { path: "/rules/terms", ...page(<TermsPage />) },
      { path: "/rules/sensitive", ...page(<SensitivePhrasesPage />) },
      { path: "/rules/suggestions", ...page(<SuggestionTemplatesPage />) },
      { path: "/rules/versions", ...page(<RuleVersionsPage />) },
    ],
  },
  {
    element: <RequireRole allow="stats" />,
    children: [
      { path: "/stats/overview", ...page(<StatsOverviewPage />) },
      { path: "/stats/ai-quality", ...page(<AiQualityPage />) },
    ],
  },
  {
    element: <RequireRole allow="export" />,
    children: [{ path: "/stats/export", ...page(<ExportPage />) }],
  },
  {
    element: <RequireRole allow="batches" />,
    children: [{ path: "/admin/batches", ...page(<BatchesPage />) }],
  },
  {
    element: <RequireRole allow="orgs" />,
    children: [{ path: "/admin/orgs", ...page(<OrgsPage />) }],
  },
  {
    element: <RequireRole allow="users" />,
    children: [{ path: "/admin/users", ...page(<UsersPage />) }],
  },
  {
    element: <RequireRole allow="settings" />,
    children: [{ path: "/admin/settings", ...page(<SettingsPage />) }],
  },
  {
    element: <RequireRole allow="audit" />,
    children: [{ path: "/admin/audit-logs", ...page(<AuditLogsPage />) }],
  },
  { path: "*", ...page(<NotFoundPage />) },
]

// 根路由的错误页占满整屏（登录、改密、选择身份及外壳本身）；外壳内的页面出错时
// 由无路径的中间路由接住，只替换内容区，菜单和顶栏保留
export const appRoutes = [{
  errorElement: <RouteError fullPage />,
  children: [
    { path: "/login", element: <Gate><LoginPage /></Gate> },
    {
      element: <RequireAuth />,
      children: [
        { path: "/change-password", element: <Gate><ChangePasswordPage /></Gate> },
        { path: "/choose-identity", element: <Gate><ChooseIdentityPage /></Gate> },
        {
          element: <RequireIdentity />,
          children: [{
            element: <Gate><LazyShell /></Gate>,
            children: [{ errorElement: <RouteError />, children: shellPages }],
          }],
        },
      ],
    },
  ],
}]
