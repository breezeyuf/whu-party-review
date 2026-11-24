import { Cell, Pie, PieChart as RCPie, ResponsiveContainer, Tooltip } from "recharts"
import { COLORS } from "./chartTheme"

export function PieChart({ data = [], nameKey = "name", valueKey = "value", height = 240 }) {
  const total = data.reduce((sum, item) => sum + (Number(item[valueKey]) || 0), 0)
  return (
    <div>
      {data.length && total > 0 ? <>
        <div style={{ width: "100%", height }}>
          <ResponsiveContainer>
            <RCPie>
              <Pie data={data} dataKey={valueKey} nameKey={nameKey} innerRadius={48} outerRadius={78} paddingAngle={2}>
                {data.map((_, i) => <Cell key={i} fill={data[i].color || COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </RCPie>
          </ResponsiveContainer>
        </div>
        <ul className="mt-2 grid grid-cols-1 gap-x-4 gap-y-2 text-xs sm:grid-cols-2" aria-label="问题类别图例">
          {data.map((item, i) => {
            const value = Number(item[valueKey]) || 0
            const share = total ? Math.round(value / total * 100) : 0
            return <li key={`${item[nameKey]}-${i}`} className="flex min-w-0 items-center gap-2">
              <span aria-hidden="true" className="h-2.5 w-2.5 shrink-0 rounded-sm" style={{ backgroundColor: item.color || COLORS[i % COLORS.length] }} />
              <span className="min-w-0 flex-1 truncate">{item[nameKey]}</span>
              <span className="mono text-base-content/65">{value} 项 · {share}%</span>
            </li>
          })}
        </ul>
      </> : <p className="flex items-center justify-center text-sm text-base-content/50" style={{ height }}>暂无问题类别数据</p>}
    </div>
  )
}
