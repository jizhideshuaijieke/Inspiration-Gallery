import http from './http'

export function getUserProfile(userId) {
  return http.get(`/users/${userId}`)
}

export function getUserArtworks(userId, params) {
  return http.get(`/users/${userId}/artworks`, { params })
}

export function getUserFollowers(userId, params) {
  return http.get(`/users/${userId}/followers`, { params })
}

export function getUserFollowing(userId, params) {
  return http.get(`/users/${userId}/following`, { params })
}

export function followUser(userId) {
  return http.post(`/users/${userId}/follow`)
}

export function unfollowUser(userId) {
  return http.delete(`/users/${userId}/follow`)
}

export function getMyNotices(params) {
  return http.get('/users/me/notices', { params })
}

export function updateMyProfile(payload) {
  return http.patch('/users/me', payload)
}

export function uploadMyAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/users/me/avatar', formData)
}
