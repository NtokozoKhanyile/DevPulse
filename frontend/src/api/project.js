import client from './client.js'

export const projectsApi = {
  create: (data) =>
    client.post('/projects', data),

  list: (params = {}) =>
    client.get('/projects', { params }),

  // Call once on mount — every call increments view_count
  getById: (id) =>
    client.get(`/projects/${id}`),

  update: (id, data) =>
    client.patch(`/projects/${id}`, data),

  delete: (id) =>
    client.delete(`/projects/${id}`),

  // Irreversible — show confirmation modal before calling
  complete: (id) =>
    client.post(`/projects/${id}/complete`),

  // Cover image upload — multipart/form-data
  uploadCover: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return client.post(`/projects/${id}/cover`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  getMilestones: (projectId) =>
    client.get(`/projects/${projectId}/milestones`),

  createMilestone: (projectId, data) =>
    client.post(`/projects/${projectId}/milestones`, data),
}