// Convert pointer coordinates on the displayed page to preview PDF points.
export function pagePoint(clientX, clientY, rect, width, height) {
  if (!rect.width || !rect.height || !(width > 0) || !(height > 0)) return null
  return [
    Math.min(width, Math.max(0, (clientX - rect.left) / rect.width * width)),
    Math.min(height, Math.max(0, (clientY - rect.top) / rect.height * height)),
  ]
}

export function regionBox(start, end) {
  return [Math.min(start[0], end[0]), Math.min(start[1], end[1]), Math.max(start[0], end[0]), Math.max(start[1], end[1])]
    .map((n) => Math.round(n * 100) / 100)
}
