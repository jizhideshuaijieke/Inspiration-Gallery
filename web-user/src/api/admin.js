import http from './http'

export function getAdminArtworks(params) {
  return http.get('/admin/artworks', { params })
}

export function hideAdminArtwork(artworkId, payload) {
  return http.patch(`/admin/artworks/${artworkId}/hide`, payload)
}

export function getAdminUsers(params) {
  return http.get('/admin/users', { params })
}

export function blockAdminUser(userId) {
  return http.patch(`/admin/users/${userId}/block`)
}

export function unblockAdminUser(userId) {
  return http.patch(`/admin/users/${userId}/unblock`)
}

export function deleteAdminComment(commentId, payload) {
  return http.delete(`/admin/comments/${commentId}`, { data: payload })
}
