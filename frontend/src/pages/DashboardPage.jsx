import PageHeader from "../components/layout/PageHeader"
import { DashboardBody } from "./dashboard/Dashboards"
import { useAuth } from "../context/AuthContext"
import { roleName } from "../utils/format"
import { useMeta } from "../context/MetaContext"

export default function DashboardPage() {
  const { user, activeRole } = useAuth()
  const meta = useMeta()
  return (
    <div>
      <PageHeader title={`你好，${user?.real_name || ""}`} crumbs={[]}>
        {roleName(meta, activeRole?.role)} · {user?.org_name || "全校"}
      </PageHeader>
      <DashboardBody />
    </div>
  )
}
