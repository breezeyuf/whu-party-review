import { CartesianGrid, Line, LineChart as RCLine, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts"
import { COLORS } from "./BarChart"

export function LineChart({ data = [], xKey = "date", lines = [], height = 240 }) {
  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <RCLine data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="oklch(0.9 0.01 250)" vertical={false} />
          <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} width={32} />
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {lines.map((l, i) => (
            <Line key={l.key} type="monotone" dataKey={l.key} name={l.name || l.key} stroke={COLORS[i % COLORS.length]} dot={data.length < 2} strokeWidth={2} />
          ))}
        </RCLine>
      </ResponsiveContainer>
    </div>
  )
}
