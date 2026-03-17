import http from './http'

export function uploadTaskInputImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/tasks/upload-input', formData)
}

export function createStyleTransferTask(payload) {
  return http.post('/tasks/style-transfer', payload)
}

export function getTask(taskId) {
  return http.get(`/tasks/${taskId}`)
}
