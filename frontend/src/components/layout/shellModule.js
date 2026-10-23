// 登录后的外壳与外壳内页面的导入清单放在同一个块里。页面从这里动态导入，打包器据此知道
// 页面总在外壳之后加载，外壳与页面共用的模块（元数据、日期格式、图标等）留在外壳块中，
// 不会拆成十几个零碎的公共文件；登录页首屏也不必携带这份清单。
export { default as Shell } from "./Shell"

export const pages = {
  DashboardPage: () => import("../../pages/DashboardPage"),
  MessagesPage: () => import("../../pages/MessagesPage"),
  ProfilePage: () => import("../../pages/ProfilePage"),
  MyProgressPage: () => import("../../pages/student/MyProgressPage"),
  MyMaterialsPage: () => import("../../pages/student/MyMaterialsPage"),
  SelfCheckPage: () => import("../../pages/student/SelfCheckPage"),
  RectificationPage: () => import("../../pages/student/RectificationPage"),
  ReviewTasksPage: () => import("../../pages/review/ReviewTasksPage"),
  ReviewWorkspacePage: () => import("../../pages/review/ReviewWorkspacePage"),
  CrossReviewConfigPage: () => import("../../pages/review/CrossReviewConfigPage"),
  JobsPage: () => import("../../pages/review/JobsPage"),
  ArchiveListPage: () => import("../../pages/archive/ArchiveListPage"),
  ArchiveDetailPage: () => import("../../pages/archive/ArchiveDetailPage"),
  BatchUploadPage: () => import("../../pages/material/BatchUploadPage"),
  MaterialDetailPage: () => import("../../pages/material/MaterialDetailPage"),
  NoticesPage: () => import("../../pages/notice/NoticesPage"),
  ChecklistsPage: () => import("../../pages/rules/ChecklistsPage"),
  MaterialTypesPage: () => import("../../pages/rules/MaterialTypesPage"),
  TimeRulesPage: () => import("../../pages/rules/TimeRulesPage"),
  CheckRulesPage: () => import("../../pages/rules/CheckRulesPage"),
  TermsPage: () => import("../../pages/rules/TermsPage"),
  SensitivePhrasesPage: () => import("../../pages/rules/SensitivePhrasesPage"),
  SuggestionTemplatesPage: () => import("../../pages/rules/SuggestionTemplatesPage"),
  RuleVersionsPage: () => import("../../pages/rules/RuleVersionsPage"),
  StatsOverviewPage: () => import("../../pages/stats/StatsOverviewPage"),
  AiQualityPage: () => import("../../pages/stats/AiQualityPage"),
  ExportPage: () => import("../../pages/stats/ExportPage"),
  BatchesPage: () => import("../../pages/admin/BatchesPage"),
  OrgsPage: () => import("../../pages/admin/OrgsPage"),
  UsersPage: () => import("../../pages/admin/UsersPage"),
  SettingsPage: () => import("../../pages/admin/SettingsPage"),
  AuditLogsPage: () => import("../../pages/admin/AuditLogsPage"),
}
