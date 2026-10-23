import { lazyWithRetry } from "../../utils/lazyLoad"

const loadShellModule = () => import("./shellModule")

export const LazyShell = lazyWithRetry(() => loadShellModule().then((module) => ({ default: module.Shell })))

// 外壳内的页面：先取外壳块里的导入清单，再下载页面本身（外壳此时通常已在内存中）。
// shellPageNames 记录路由里用到的页面名，测试据此核对每个名字都已在清单中登记
export const shellPageNames = new Set()

export function shellPage(name) {
  shellPageNames.add(name)
  return lazyWithRetry(async () => {
    const { pages } = await loadShellModule()
    if (!Object.hasOwn(pages, name)) throw new Error(`页面未在外壳清单中登记：${name}`)
    return pages[name]()
  })
}

// 登录页空闲时、或已有会话等待身份校验时预取外壳；预取失败不提示，进入工作台时会重新下载
export function preloadShell() {
  LazyShell.preload().catch(() => {})
}
