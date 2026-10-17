import { useState } from "react"

export default function JsonEditor({ value, onChange, rows = 10 }) {
  const [text, setText] = useState(() => typeof value === "string" ? value : JSON.stringify(value ?? {}, null, 2))
  const [error, setError] = useState("")

  const commit = (raw) => {
    setText(raw)
    try {
      const parsed = JSON.parse(raw)
      setError("")
      onChange?.(parsed, raw)
    } catch (e) {
      setError(e.message)
      onChange?.(undefined, raw)
    }
  }

  const format = () => {
    try {
      const parsed = JSON.parse(text)
      commit(JSON.stringify(parsed, null, 2))
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div>
      <div className="mb-1 flex justify-end">
        <button type="button" className="btn btn-ghost btn-xs" onClick={format}>格式化</button>
      </div>
      <textarea
        className={`textarea textarea-bordered w-full font-mono text-xs ${error ? "textarea-error" : ""}`}
        rows={rows}
        value={text}
        spellCheck={false}
        onChange={(e) => commit(e.target.value)}
      />
      {error && <p className="mt-1 text-xs text-error">JSON 无效：{error}</p>}
    </div>
  )
}
