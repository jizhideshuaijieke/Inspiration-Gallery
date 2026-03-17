const USER_KEY = 'admin_user'

export function setAdminSession(token, user) {
  localStorage.setItem('token', token)
  localStorage.setItem(USER_KEY, JSON.stringify(user || null))
}

export function getAdminUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch (_) {
    return null
  }
}

export function clearAdminSession() {
  localStorage.removeItem('token')
  localStorage.removeItem(USER_KEY)
}

export function hasAdminSession() {
  const token = localStorage.getItem('token')
  const user = getAdminUser()
  return Boolean(token && user && user.role === 'admin')
}
