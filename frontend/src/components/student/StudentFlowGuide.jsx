import { Link } from "react-router-dom"
import { studentFlowNotice } from "../../utils/studentFlowGuide"

export default function StudentFlowGuide({ submission, issues, groups, ready, taskPending, source, blockedReason }) {
  const step = studentFlowNotice(submission, { issues, groups, ready, taskPending })
  const samePage = source === "rectification" && step.to === "/my/rectification"
  return <section aria-label="当前办理指引" className="surface-card mb-4 flex flex-wrap items-center justify-between gap-3 border-l-4 border-l-primary p-4" role="status">
    <div className="min-w-0"><h2 className="text-sm font-semibold">{step.title}</h2><p className="mt-1 text-xs leading-relaxed text-base-content/65">{blockedReason || step.description}</p></div>
    {step.to && !samePage && <Link className="btn btn-outline btn-sm shrink-0" to={step.to}>{step.label}</Link>}
  </section>
}
