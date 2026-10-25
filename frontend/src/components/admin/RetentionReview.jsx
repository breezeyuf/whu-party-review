import { useState } from "react"
import { listExpiredMaterials, keepExpiredMaterial } from "../../api/settings"

export default function RetentionReview() {
  const [data,setData]=useState(null)
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState("")
  const [status,setStatus]=useState("pending")
  const [reason,setReason]=useState("经核对继续保留原件")
  const load=async (page=1,selected=status) => {
    setBusy(true); setError("")
    try { setData(await listExpiredMaterials({page,page_size:20,status:selected})); setStatus(selected) }
    catch(e) { setError(e.message || "清单加载失败") }
    finally { setBusy(false) }
  }
  return <section className="surface-card space-y-3 p-4">
    <h2 className="text-sm font-medium">到期材料待处理清单</h2>
    <p className="text-xs">按已保存的材料保留年数和版本上传日期计算。确认仅记录继续保留，不删除或移动原件。</p>
    <div className="flex gap-2"><button className="btn btn-outline btn-sm" disabled={busy} onClick={()=>load(1,"pending")}>查看到期待处理材料</button><button className="btn btn-ghost btn-sm" disabled={busy} onClick={()=>load(1,"confirmed")}>查看已确认保留</button></div>
    {error && <p role="alert" className="text-error text-xs">{error}</p>}
    {data && <>
      <p className="text-xs">{status==="pending" ? "待处理" : "已确认保留"} {data.total} 个版本 · 保留期限 {data.material_years} 年</p>
      {status==="pending" && <label className="form-control text-xs">保留原因<input aria-label="到期材料保留原因" className="input input-bordered input-sm" value={reason} maxLength={500} onChange={e=>setReason(e.target.value)} /></label>}
      {!data.items.length && <p className="text-xs">暂无符合条件的材料。</p>}
      {data.items.map(row=><div key={row.id} className="flex items-center justify-between gap-3 border-t border-base-300 pt-2 text-xs">
        <span>{row.title} · {row.filename} · 第 {row.version_no} 版 · 到期 {row.due_at.slice(0,10)}</span>
        {status==="pending" && <button className="btn btn-outline btn-xs" disabled={busy || !reason.trim()} onClick={async()=>{
          setBusy(true); setError("")
          try { await keepExpiredMaterial(row.id,{reason}); await load(data.page) }
          catch(e) { setError(e.message || "确认失败") }
          finally { setBusy(false) }
        }}>确认保留原件</button>}
      </div>)}
      <div className="flex items-center gap-3 text-xs"><button className="btn btn-ghost btn-xs" disabled={busy || data.page<=1} onClick={()=>load(data.page-1)}>上一页</button><span>第 {data.page} 页</span><button className="btn btn-ghost btn-xs" disabled={busy || data.page*data.page_size>=data.total} onClick={()=>load(data.page+1)}>下一页</button></div>
    </>}
  </section>
}
