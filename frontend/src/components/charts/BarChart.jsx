import { Bar, BarChart as RCBar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const COLORS = ["#b4222a", "#6f6257", "#a8781f", "#4a7c74", "#a34a3a", "#7a7f4e", "#c2a878", "#5a6472"]

function ellipsis(v, max = 8) {
  const s = String(v ?? "")
  return s.length > max ? `${s.slice(0, max)}…` : s
}

export function BarChart({ data = [], xKey = "name", yKey = "value", height = 240, maxTickLength = 8 }) {
  const maxLen = Math.max(0, ...data.map((d) => String(d[xKey] ?? "").length))
  const tilted = data.length > 5 || maxLen > 6
  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <RCBar data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="oklch(0.9 0.01 250)" vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 11 }}
            interval={0}
            angle={tilted ? -18 : 0}
            textAnchor={tilted ? "end" : "middle"}
            height={tilted ? 54 : 30}
            tickFormatter={(v) => ellipsis(v, maxTickLength)}
          />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} width={32} />
          <Tooltip />
          <Bar dataKey={yKey} fill={COLORS[0]} radius={[4, 4, 0, 0]} maxBarSize={36} />
        </RCBar>
      </ResponsiveContainer>
    </div>
  )
}

export { COLORS }
