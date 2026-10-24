import { Component, Suspense } from "react"
import { isChunkLoadError, lazyWithRetry, resetFailedLazy } from "../../utils/lazyLoad"

// 与原图表同名、同参数；recharts 在图表区渲染时才下载，数据卡片和表格先显示
const LazyBar = lazyWithRetry(() => import("./BarChart").then((m) => ({ default: m.BarChart })))
const LazyPie = lazyWithRetry(() => import("./PieChart").then((m) => ({ default: m.PieChart })))
const LazyLine = lazyWithRetry(() => import("./LineChart").then((m) => ({ default: m.LineChart })))

function ChartPlaceholder({ height }) {
  return (
    <div role="status" aria-live="polite" className="skeleton flex w-full items-center justify-center text-xs text-base-content/55" style={{ height }}>
      正在加载图表…
    </div>
  )
}

// 图表文件下载失败只影响图表区；点“重新加载”就地重新下载，不刷新整页
class ChartBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  retry = () => {
    resetFailedLazy()
    this.setState({ error: null })
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children
    return (
      <div role="alert" className="flex w-full flex-col items-center justify-center gap-2 rounded-box border border-error/30 bg-error/5 p-4 text-center text-xs" style={{ minHeight: this.props.height }}>
        <p className="font-medium text-error">图表加载失败</p>
        <p className="text-base-content/60">{isChunkLoadError(error) ? "图表文件下载失败，可能是网络中断或系统刚刚更新。" : error.message || "图表渲染出错"}</p>
        <button type="button" className="btn btn-outline btn-xs" onClick={this.retry}>重新加载</button>
      </div>
    )
  }
}

function withChart(Lazy) {
  return function LazyChart(props) {
    const height = props.height ?? 240
    return (
      <ChartBoundary height={height}>
        <Suspense fallback={<ChartPlaceholder height={height} />}><Lazy {...props} /></Suspense>
      </ChartBoundary>
    )
  }
}

export const BarChart = withChart(LazyBar)
export const PieChart = withChart(LazyPie)
export const LineChart = withChart(LazyLine)
