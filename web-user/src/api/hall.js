import http from './http'

export function getHallFeed(params) {
  return http.get('/hall/feed', { params })
}
