import { Cell, Pie, PieChart as RCPie, ResponsiveContainer, Tooltip } from "recharts"
import { COLORS } from "./BarChart"

export function PieChart({ data = [], nameKey = "name", valueKey = "value", height = 240 }) {
  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <RCPie>
          <Pie data={data} dataKey={valueKey} nameKey={nameKey} innerRadius={48} outerRadius={78} paddingAngle={2}>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip />
        </RCPie>
      </ResponsiveContainer>
    </div>
  )
}
