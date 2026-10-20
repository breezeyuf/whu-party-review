import { Link } from "react-router-dom"
import { useMeta } from "../../context/MetaContext"
import { stageName, statusName } from "../../utils/format"
import { StatusBadge } from "../common/Badges"

export default function StageProgress({ stages = [], current, submissionBase = "/review/submissions" }) {
  const meta = useMeta()
  const list = (meta.stages || []).map((s) => {
    const hit = stages.find((x) => Number(x.code) === Number(s.code))
    return { ...s, ...(hit || {}) }
  })
  return (
    <ul className="steps steps-horizontal w-full text-xs">
      {list.map((s) => {
        const done = s.status === "FILED" || (current && Number(s.code) < Number(current))
        const active = Number(s.code) === Number(current)
        return (
          <li key={s.code} className={`step ${done || active ? "step-primary" : ""}`}>
            <span className="mt-1 block max-w-28 leading-tight">
              {stageName(meta, s.code)}
              {s.status && (
                <span className="mt-1 block">
                  {s.submission_id ? (
                    <Link to={`${submissionBase}/${s.submission_id}`} className="link"><StatusBadge code={s.status} /></Link>
                  ) : <StatusBadge code={s.status} />}
                </span>
              )}
              {!s.status && active && <span className="mt-1 block text-primary">当前</span>}
            </span>
          </li>
        )
      })}
    </ul>
  )
}
