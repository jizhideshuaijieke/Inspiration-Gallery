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

export function deleteAdminComment(commentId, payload) {
  return http.delete(`/admin/comments/${commentId}`, { data: payload })
}
