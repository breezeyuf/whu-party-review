import { Suspense } from "react"
import { Outlet } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"
import { MetaProvider } from "../../context/MetaContext"
import { Loading } from "../common/States"
import { roleKey } from "../../utils/identity"
import AppLayout from "./AppLayout"

// 登录后的外壳（元数据、菜单、未读消息轮询）单独成块，登录页首屏不下载
export default function Shell() {
  const { user, activeRole } = useAuth()
  return (
    <MetaProvider key={`${user.id}:${roleKey(activeRole)}`}>
      <AppLayout>
        <Suspense fallback={<Loading />}><Outlet /></Suspense>
      </AppLayout>
    </MetaProvider>
  )
}
