import http from './http'

export function getStyles() {
  return http.get('/styles')
}
