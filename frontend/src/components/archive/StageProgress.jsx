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
    <div>
    <ul className="steps steps-horizontal w-full min-w-[38rem] text-xs">
      {list.map((s) => {
        const done = s.status === "FILED" || (current && Number(s.code) < Number(current))
        const active = Number(s.code) === Number(current)
        return (
          <li key={s.code} className={`step ${done ? "step-primary" : active ? "step-primary" : ""}`}>
            <span className={`mt-1 block max-w-28 leading-tight ${active ? "font-semibold text-primary" : done ? "text-base-content/75" : "text-base-content/45"}`}>
              <span>{stageName(meta, s.code)}</span>
              {s.status && (
                <span className="mt-1 block">
                  {s.submission_id ? (
                    <Link to={`${submissionBase}/${s.submission_id}`} className="link"><StatusBadge code={s.status} /></Link>
                  ) : <StatusBadge code={s.status} />}
                </span>
              )}
              {!s.status && active && <span className="mt-1 inline-flex rounded-full bg-primary/10 px-2 py-0.5 text-[10px] text-primary">当前阶段</span>}
              {!s.status && !active && !done && <span className="mt-1 block text-[10px] text-base-content/40">待进入</span>}
            </span>
          </li>
        )
      })}
    </ul>
    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-base-content/55" aria-label="阶段进度说明">
      <span className="inline-flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-primary" />已完成 / 当前</span>
      <span className="inline-flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-base-300" />待进入</span>
    </div>
    </div>
  )
}
