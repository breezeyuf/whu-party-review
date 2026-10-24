import PageHeader from "../components/layout/PageHeader"
import { DashboardBody } from "./dashboard/Dashboards"
import { useAuth } from "../context/AuthContext"
import { roleName } from "../utils/format"
import { useMeta } from "../context/MetaContext"
import { activeOrganization, identityFor } from "../utils/identity"

export default function DashboardPage() {
  const { user, activeRole } = useAuth()
  const meta = useMeta()
  return (
    <div>
      <PageHeader title={activeRole?.role === "STUDENT" ? "我的办理事项" : identityFor(activeRole)?.kind === "admin" ? "管理工作台" : "审核工作台"} crumbs={[]}>
        {user?.real_name || ""} · {roleName(meta, activeRole?.role)} · {activeOrganization(user)}
      </PageHeader>
      <DashboardBody />
    </div>
  )
}
