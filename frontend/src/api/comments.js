import client from './client.js'

export const commentsApi = {
  list: (projectId, params = {}) =>
    client.get(`/projects/${projectId}/comments`, { params }),

  // parent_id is optional — omit for top-level comments
  post: (projectId, data) =>
    client.post(`/projects/${projectId}/comments`, data),

  edit: (projectId, commentId, body) =>
    client.patch(`/projects/${projectId}/comments/${commentId}`, { body }),

  // Soft delete — comment remains visible as "[comment deleted]"
  delete: (projectId, commentId) =>
    client.delete(`/projects/${projectId}/comments/${commentId}`),
}