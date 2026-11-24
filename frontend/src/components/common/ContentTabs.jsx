export default function ContentTabs({ items, value, onChange, label, idPrefix }) {
  const onKey = (event, index) => {
    const next = event.key === "Home" ? 0 : event.key === "End" ? items.length - 1 : event.key === "ArrowRight" ? (index + 1) % items.length : event.key === "ArrowLeft" ? (index - 1 + items.length) % items.length : null
    if (next == null) return
    event.preventDefault()
    onChange(items[next][0])
    event.currentTarget.parentElement.querySelectorAll('[role="tab"]')[next].focus()
  }
  return <div className="content-tabs" role="tablist" aria-label={label}>
    {items.map(([key, text], index) => <button key={key} id={`${idPrefix}-${key}`} type="button" role="tab" aria-selected={value === key} aria-controls={`${idPrefix}-panel-${key}`} tabIndex={value === key ? 0 : -1} className="content-tab" onClick={() => onChange(key)} onKeyDown={e => onKey(e, index)}>{text}</button>)}
  </div>
}
