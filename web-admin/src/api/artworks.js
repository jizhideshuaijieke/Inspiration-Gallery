import http from './http'

export function getArtworkDetail(artworkId) {
  return http.get(`/artworks/${artworkId}`)
}

export function getArtworkComments(artworkId, params) {
  return http.get(`/artworks/${artworkId}/comments`, { params })
}
