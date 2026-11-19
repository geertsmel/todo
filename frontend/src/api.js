// Appel de l'API (nginx redirige /api vers le backend)
export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : `Erreur ${response.status}`)
  }
  return response.status === 204 ? null : response.json()
}
