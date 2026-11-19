import { STATUSES } from './statuses.js'

const round = (n) => Math.round(n * 100) / 100

// Calcule les parts du camembert à partir du nombre de tâches par statut.
// Chaque part contient son tracé SVG (path), ou full = true si elle occupe tout le disque.
export function buildSlices(counts, cx = 100, cy = 100, r = 90) {
  const total = STATUSES.reduce((sum, s) => sum + (counts[s.key] || 0), 0)
  if (total === 0) return []

  let angle = -Math.PI / 2 // on part du haut du cercle
  return STATUSES.filter((s) => counts[s.key] > 0).map((s) => {
    const value = counts[s.key]
    const fraction = value / total
    const percent = Math.round(fraction * 100)
    if (fraction === 1) return { ...s, value, percent, full: true }

    const start = angle
    const end = angle + fraction * 2 * Math.PI
    angle = end
    const x1 = round(cx + r * Math.cos(start))
    const y1 = round(cy + r * Math.sin(start))
    const x2 = round(cx + r * Math.cos(end))
    const y2 = round(cy + r * Math.sin(end))
    const largeArc = fraction > 0.5 ? 1 : 0
    return { ...s, value, percent, path: `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z` }
  })
}
