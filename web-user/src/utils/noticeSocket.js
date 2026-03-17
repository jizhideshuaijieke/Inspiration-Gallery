const API_BASE_URL = (process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function buildNoticeSocketUrl(token) {
  const wsBase = API_BASE_URL.replace(/^http/i, 'ws')
  const query = token ? `?token=${encodeURIComponent(token)}` : ''
  return `${wsBase}/users/ws/notices${query}`
}

export function createNoticeSocket({ token, onMessage, onClose, onError } = {}) {
  if (typeof WebSocket === 'undefined') return null

  const socket = new WebSocket(buildNoticeSocketUrl(token))

  socket.onmessage = (event) => {
    if (!onMessage) return

    try {
      onMessage(JSON.parse(event.data))
    } catch (_) {
      // Keep the socket alive and ignore malformed payloads.
    }
  }

  if (onClose) socket.onclose = onClose
  if (onError) socket.onerror = onError

  return socket
}
