import client from './client.js'

export const usersApi = {
  me: () =>
    client.get('/users/me'),

  updateProfile: (data) =>
    client.patch('/users/me', data),

  // Avatar upload — multipart/form-data
  uploadAvatar: (file) => {
    const form = new FormData()
    form.append('file', file)
    return client.post('/users/me/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  getByUsername: (username) =>
    client.get(`/users/${username}`),

  getUserProjects: (username, params = {}) =>
    client.get(`/users/${username}/projects`, { params }),
}