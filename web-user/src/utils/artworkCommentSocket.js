const API_BASE_URL = (process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function buildArtworkCommentSocketUrl(artworkId, token) {
  const wsBase = API_BASE_URL.replace(/^http/i, 'ws')
  const query = token ? `?token=${encodeURIComponent(token)}` : ''
  return `${wsBase}/artworks/${artworkId}/comments/ws${query}`
}

export function createArtworkCommentSocket(
  artworkId,
  { token, onMessage, onClose, onError } = {}
) {
  if (!artworkId || typeof WebSocket === 'undefined') return null

  const socket = new WebSocket(buildArtworkCommentSocketUrl(artworkId, token))

  socket.onmessage = (event) => {
    if (!onMessage) return

    try {
      onMessage(JSON.parse(event.data))
    } catch (_) {
      // Ignore malformed payloads and keep the current detail usable.
    }
  }

  if (onClose) socket.onclose = onClose
  if (onError) socket.onerror = onError

  return socket
}
