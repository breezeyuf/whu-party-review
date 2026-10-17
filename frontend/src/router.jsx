import { Navigate, Outlet, createBrowserRouter, useLocation } from "react-router-dom"
import { lazy, Suspense } from "react"
import { useAuth } from "./context/AuthContext"
import { MetaProvider } from "./context/MetaContext"
import AppLayout from "./components/layout/AppLayout"
import { Loading } from "./components/common/States"
import { ForbiddenPage, NotFoundPage } from "./pages/StatusPages"
import { can } from "./utils/permissions"

const LoginPage = lazy(() => import("./pages/LoginPage"))
const ChangePasswordPage = lazy(() => import("./pages/ChangePasswordPage"))
const DashboardPage = lazy(() => import("./pages/DashboardPage"))
const MessagesPage = lazy(() => import("./pages/MessagesPage"))
const ProfilePage = lazy(() => import("./pages/ProfilePage"))
const MyProgressPage = lazy(() => import("./pages/student/MyProgressPage"))
const MyMaterialsPage = lazy(() => import("./pages/student/MyMaterialsPage"))
const SelfCheckPage = lazy(() => import("./pages/student/SelfCheckPage"))
const RectificationPage = lazy(() => import("./pages/student/RectificationPage"))
const ReviewTasksPage = lazy(() => import("./pages/review/ReviewTasksPage"))
const ReviewWorkspacePage = lazy(() => import("./pages/review/ReviewWorkspacePage"))
const CrossReviewConfigPage = lazy(() => import("./pages/review/CrossReviewConfigPage"))
const JobsPage = lazy(() => import("./pages/review/JobsPage"))
const ArchiveListPage = lazy(() => import("./pages/archive/ArchiveListPage"))
const ArchiveDetailPage = lazy(() => import("./pages/archive/ArchiveDetailPage"))
const BatchUploadPage = lazy(() => import("./pages/material/BatchUploadPage"))
const MaterialDetailPage = lazy(() => import("./pages/material/MaterialDetailPage"))
const NoticesPage = lazy(() => import("./pages/notice/NoticesPage"))
const ChecklistsPage = lazy(() => import("./pages/rules/ChecklistsPage"))
const MaterialTypesPage = lazy(() => import("./pages/rules/MaterialTypesPage"))
const TimeRulesPage = lazy(() => import("./pages/rules/TimeRulesPage"))
const CheckRulesPage = lazy(() => import("./pages/rules/CheckRulesPage"))
const TermsPage = lazy(() => import("./pages/rules/TermsPage"))
const SensitivePhrasesPage = lazy(() => import("./pages/rules/SensitivePhrasesPage"))
const SuggestionTemplatesPage = lazy(() => import("./pages/rules/SuggestionTemplatesPage"))
const RuleVersionsPage = lazy(() => import("./pages/rules/RuleVersionsPage"))
const StatsOverviewPage = lazy(() => import("./pages/stats/StatsOverviewPage"))
const AiQualityPage = lazy(() => import("./pages/stats/AiQualityPage"))
const ExportPage = lazy(() => import("./pages/stats/ExportPage"))
const BatchesPage = lazy(() => import("./pages/admin/BatchesPage"))
const OrgsPage = lazy(() => import("./pages/admin/OrgsPage"))
const UsersPage = lazy(() => import("./pages/admin/UsersPage"))
const SettingsPage = lazy(() => import("./pages/admin/SettingsPage"))
const AuditLogsPage = lazy(() => import("./pages/admin/AuditLogsPage"))

function Gate({ children }) {
  return <Suspense fallback={<Loading />}>{children}</Suspense>
}

function RequireAuth() {
  const { user, ready } = useAuth()
  const loc = useLocation()
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

function Shell() {
  return (
    <MetaProvider>
      <AppLayout>
        <Gate><Outlet /></Gate>
      </AppLayout>
    </MetaProvider>
  )
}

const page = (el) => ({ element: el })

export const router = createBrowserRouter([
  { path: "/login", element: <Gate><LoginPage /></Gate> },
  {
    element: <RequireAuth />,
    children: [
      { path: "/change-password", element: <Gate><ChangePasswordPage /></Gate> },
      {
        element: <Shell />,
        children: [
          { path: "/", ...page(<DashboardPage />) },
          { path: "/messages", ...page(<MessagesPage />) },
          { path: "/profile", ...page(<ProfilePage />) },
          { path: "/403", ...page(<ForbiddenPage />) },
          { path: "/my/progress", ...page(<MyProgressPage />) },
          { path: "/my/materials", ...page(<MyMaterialsPage />) },
          { path: "/my/self-check/:submissionId", ...page(<SelfCheckPage />) },
          { path: "/my/rectification", ...page(<RectificationPage />) },
          { path: "/materials/:id", ...page(<MaterialDetailPage />) },
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
        ],
      },
    ],
  },
])
