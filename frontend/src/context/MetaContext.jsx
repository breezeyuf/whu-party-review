import { displaySeverities } from "../utils/reviewTerms"
import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { getMeta } from "../api/meta"
import { FALLBACK_META } from "../utils/constants"
import { useAuth } from "./AuthContext"

const MetaContext = createContext(null)

export function MetaProvider({ children }) {
  const { user } = useAuth()
  const [meta, setMeta] = useState(FALLBACK_META)

  useEffect(() => {
    if (!user) return
    let alive = true
    getMeta().then((data) => {
      if (!alive || !data) return
      setMeta({ ...FALLBACK_META, ...data, severities: displaySeverities(data.severities || FALLBACK_META.severities) })
    }).catch(() => {})
    return () => { alive = false }
  }, [user])

  const value = useMemo(() => meta, [meta])
  return <MetaContext.Provider value={value}>{children}</MetaContext.Provider>
}

export function useMeta() {
  return useContext(MetaContext) || FALLBACK_META
}
