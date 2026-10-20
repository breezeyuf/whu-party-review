import { useRef, useState } from "react"

const ACCEPT = ".pdf,.jpg,.jpeg,.png,.docx,.zip"

export default function FileUploader({
  accept = ACCEPT,
  maxMb = 20,
  label = "选择文件",
  hint,
  disabled,
  compact = false,
  onFile,
}) {
  const inputRef = useRef(null)
  const uploading = useRef(false)
  const [drag, setDrag] = useState(false)
  const [error, setError] = useState("")
  const [progress, setProgress] = useState(null)

  const check = (file) => {
    if (!file || disabled || uploading.current) return
    const ext = `.${(file.name.split(".").pop() || "").toLowerCase()}`
    const allowed = accept.split(",").map((s) => s.trim().toLowerCase())
    if (!allowed.includes(ext)) {
      setError(`不支持的格式 ${ext}，允许 ${accept}`)
      return
    }
    if (file.size > maxMb * 1024 * 1024) {
      setError(`文件超过 ${maxMb} MB`)
      return
    }
    setError("")
    uploading.current = true
    setProgress(0)
    Promise.resolve().then(() => onFile(file, setProgress))
      .catch((e) => setError(e?.message || "上传失败"))
      .finally(() => { uploading.current = false; setProgress(null) })
  }

  return (
    <div>
      <div
        className={`${compact ? "service-compact-upload" : "rounded-lg border border-dashed px-4 py-6 text-center"} ${drag ? "border-primary bg-base-200" : "border-base-300"} ${disabled ? "opacity-50" : ""}`}
        onDragOver={(e) => { e.preventDefault(); if (!disabled) setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); if (!disabled) check(e.dataTransfer.files?.[0]) }}
      >
        <p className="text-sm">{hint || "拖拽文件到此处，或点击选择"}</p>
        <button type="button" className="btn btn-primary btn-sm mt-3" disabled={disabled || progress != null} onClick={() => inputRef.current?.click()}>
          {label}
        </button>
        <input
          ref={inputRef}
          type="file"
          disabled={disabled || progress != null}
          accept={accept}
          className="hidden"
          onChange={(e) => { check(e.target.files?.[0]); e.target.value = "" }}
        />
        {progress != null && (
          <progress className="progress progress-primary mt-3 w-full" value={progress} max="100" />
        )}
      </div>
      {error && <p className="mt-2 text-xs text-error">{error}</p>}
    </div>
  )
}
