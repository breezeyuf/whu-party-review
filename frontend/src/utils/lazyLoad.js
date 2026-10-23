import { createElement, lazy } from "react"

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// 浏览器与 Vite 对“页面文件下载失败”的几种说法（断网、发版后旧文件失效）
const CHUNK_ERROR = /Failed to fetch dynamically imported module|error loading dynamically imported module|Importing a module script failed|Unable to preload CSS|Loading (CSS )?chunk .+ failed/i

export function isChunkLoadError(error) {
  if (!error) return false
  return error.isChunkLoadError === true || CHUNK_ERROR.test(String(error.message || error))
}

function markLoadError(error) {
  const err = error instanceof Error ? error : new Error(String(error))
  err.isChunkLoadError = true
  return err
}

// 下载失败时等待片刻再试；重试仍失败才抛出，交给路由或图表的错误边界
export async function loadWithRetry(factory, { retries = 1, delay = 600 } = {}) {
  for (let attempt = 0; ; attempt += 1) {
    try {
      return await factory()
    } catch (error) {
      if (attempt >= retries) throw markLoadError(error)
      await wait(delay)
    }
  }
}

// 已下载的模块用同步 thenable 交给 React.lazy，预取过的组件渲染时不再闪一次加载占位
const settled = (module) => ({ then: (resolve) => resolve(module) })

// React.lazy 会永久记住一次失败。错误提示展示后再换成新实例，下次进入时重新下载；
// 不能在失败的当下就换，否则 Suspense 重试时会立即重新下载，错误永远显示不出来
const failed = new Map()

export function resetFailedLazy() {
  for (const reset of failed.values()) reset()
  failed.clear()
}

export function lazyWithRetry(factory, options) {
  let loaded = null
  let pending = null
  const preload = () => {
    if (loaded) return Promise.resolve(loaded)
    if (!pending) {
      pending = loadWithRetry(factory, options).then(
        (module) => { loaded = module; return module },
        (error) => { pending = null; throw error },
      )
    }
    return pending
  }
  const create = () => lazy(() => (loaded ? settled(loaded) : preload().catch((error) => {
    failed.set(LazyComponent, () => { current = create() })
    throw error
  })))
  let current = create()
  function LazyComponent(props) {
    return createElement(current, props)
  }
  // 预取与渲染共用同一个下载；预取失败不缓存，之后渲染会重新下载
  LazyComponent.preload = preload
  return LazyComponent
}

// 空闲时执行低优先级工作（如预取）；不支持 requestIdleCallback 的浏览器退回定时器
export function whenIdle(callback, fallbackDelay = 200) {
  if (typeof window !== "undefined" && typeof window.requestIdleCallback === "function") {
    const handle = window.requestIdleCallback(callback, { timeout: 2000 })
    return () => window.cancelIdleCallback?.(handle)
  }
  const timer = setTimeout(callback, fallbackDelay)
  return () => clearTimeout(timer)
}
