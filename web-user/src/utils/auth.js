function parseJwtPayload(token) {
  if (!token || typeof token !== 'string') return null
  const segments = token.split('.')
  if (segments.length < 2) return null

  try {
    const base64 = segments[1].replace(/-/g, '+').replace(/_/g, '/')
    const pad = '='.repeat((4 - (base64.length % 4)) % 4)
    const json = atob(base64 + pad)
    return JSON.parse(json)
  } catch (_) {
    return null
  }
}

export function getCurrentUserIdFromToken() {
  const token = localStorage.getItem('token')
  const payload = parseJwtPayload(token)
  const rawId = payload && payload.sub
  const userId = Number(rawId)
  return Number.isInteger(userId) && userId > 0 ? userId : null
}

export function getCurrentUserRoleFromToken() {
  const token = localStorage.getItem('token')
  const payload = parseJwtPayload(token)
  return payload && typeof payload.role === 'string' ? payload.role : ''
}

export function isAdminToken() {
  return getCurrentUserRoleFromToken() === 'admin'
}
