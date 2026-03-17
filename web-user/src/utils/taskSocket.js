const API_BASE_URL = (process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function buildTaskSocketUrl(taskId, token) {
  const wsBase = API_BASE_URL.replace(/^http/i, 'ws')
  const query = token ? `?token=${encodeURIComponent(token)}` : ''
  return `${wsBase}/tasks/ws/${taskId}${query}`
}

export function createTaskSocket(taskId, { token, onMessage, onClose, onError } = {}) {
  if (!taskId || typeof WebSocket === 'undefined') return null

  const socket = new WebSocket(buildTaskSocketUrl(taskId, token))

  socket.onmessage = (event) => {
    if (!onMessage) return

    try {
      onMessage(JSON.parse(event.data))
    } catch (_) {
      // Ignore malformed payloads and keep the fallback polling available.
    }
  }

  if (onClose) socket.onclose = onClose
  if (onError) socket.onerror = onError

  return socket
}
