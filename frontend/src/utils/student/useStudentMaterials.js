import { useEffect, useRef } from "react"
import { listMaterials } from "../../api/materials"
import { useRequest } from "../../hooks/useRequest"
import { pendingParseCount } from "../studentWorkflow"

export function useStudentMaterials(archiveId, stageCode, onParsed) {
  const request = useRequest(() => archiveId ? listMaterials(archiveId, { stage_code: stageCode }) : [], [archiveId, stageCode], { immediate: !!archiveId })
  const pending = pendingParseCount(request.data || [])
  const wasPending = useRef(false)
  const callback = useRef(onParsed)
  useEffect(() => { callback.current = onParsed }, [onParsed])
  useEffect(() => { wasPending.current = false }, [archiveId, stageCode])
  useEffect(() => {
    if (request.loading || request.error) return undefined
    if (wasPending.current && !pending) callback.current?.()
    wasPending.current = pending > 0
    if (!pending) return undefined
    const timer = setTimeout(() => request.reload().catch(() => {}), 2000)
    return () => clearTimeout(timer)
  }, [pending, request.loading, request.error, request.reload])
  return { ...request, pending }
}
