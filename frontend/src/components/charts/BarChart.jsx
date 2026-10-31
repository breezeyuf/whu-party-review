import { Bar, BarChart as RCBar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell, LabelList } from "recharts"
import { COLORS } from "./chartTheme"

function ellipsis(v, max = 8) {
  const s = String(v ?? "")
  return s.length > max ? `${s.slice(0, max)}…` : s
}

export function BarChart({ data = [], xKey = "name", yKey = "value", height = 240, maxTickLength = 8, horizontal = false, color = COLORS[0] }) {
  const maxLen = Math.max(0, ...data.map(d => String(d[xKey] ?? "").length))
  const tilted = !horizontal && (data.length > 5 || maxLen > 6)
  if (!data.length) return <p className="flex items-center justify-center text-sm text-base-content/55" style={{ height }}>暂无统计数据</p>
  return <div style={{ width: "100%", height }}>
    <ResponsiveContainer>
      <RCBar data={data} layout={horizontal ? "vertical" : "horizontal"} margin={{ top: 16, right: 32, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#E6EBEF" vertical={horizontal} horizontal={!horizontal} strokeDasharray="3 3" />
        <XAxis type={horizontal ? "number" : "category"} dataKey={horizontal ? undefined : xKey} domain={horizontal ? [0, "auto"] : undefined} tick={{ fontSize: 11, fill: "#637383" }} axisLine={false} tickLine={false} interval={0} allowDecimals={false} angle={tilted ? -18 : 0} textAnchor={tilted ? "end" : "middle"} height={tilted ? 54 : 30} tickFormatter={horizontal ? undefined : v => ellipsis(v, maxTickLength)} />
        <YAxis type={horizontal ? "category" : "number"} dataKey={horizontal ? xKey : undefined} domain={horizontal ? undefined : [0, "auto"]} interval={horizontal ? 0 : undefined} tick={{ fontSize: 11, fill: "#637383" }} axisLine={false} tickLine={false} allowDecimals={false} width={horizontal ? 144 : 32} tickFormatter={horizontal ? v => ellipsis(v, maxTickLength) : undefined} />
        <Tooltip cursor={{ fill: "#EDF2F6" }} />
        <Bar dataKey={yKey} name="数量" fill={color} radius={horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]} maxBarSize={32}>
          {data.map((item, i) => <Cell key={item.code || item[xKey] || i} fill={item.color || color} />)}
          <LabelList dataKey={yKey} position={horizontal ? "right" : "top"} style={{ fill: "#506173", fontSize: 11 }} />
        </Bar>
      </RCBar>
    </ResponsiveContainer>
  </div>
}

export { COLORS }
