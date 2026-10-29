export async function loadOptions(fetchPage) {
  const first = await fetchPage({page: 1, page_size: 100})
  const rows = [...(first.items || [])]
  for (let page = 2; rows.length < (first.total || 0); page++) {
    const next = await fetchPage({page, page_size: 100})
    if (!next.items?.length) throw new Error("Incomplete options")
    rows.push(...next.items)
  }
  return rows
}
