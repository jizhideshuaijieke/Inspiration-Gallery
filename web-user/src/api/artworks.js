import http from './http'

export function createArtwork(payload) {
  return http.post('/artworks', payload)
}

export function updateArtwork(artworkId, payload) {
  return http.patch(`/artworks/${artworkId}`, payload)
}

export function getArtworkDetail(artworkId) {
  return http.get(`/artworks/${artworkId}`)
}

export function getArtworkComments(artworkId, params) {
  return http.get(`/artworks/${artworkId}/comments`, { params })
}

export function postArtworkComment(artworkId, payload) {
  return http.post(`/artworks/${artworkId}/comments`, payload)
}

export function likeArtwork(artworkId) {
  return http.post(`/artworks/${artworkId}/like`)
}

export function unlikeArtwork(artworkId) {
  return http.delete(`/artworks/${artworkId}/like`)
}

export function deleteArtwork(artworkId) {
  return http.delete(`/artworks/${artworkId}`)
}
