import client from './client.js'

export const authApi = {
  register: (data) =>
    client.post('/auth/register', data),

  login: (data) =>
    client.post('/auth/login', data),

  // Refresh token goes in the body — not the Authorization header
  refresh: (refreshToken) =>
    client.post('/auth/refresh', { refresh_token: refreshToken }),

  logout: () =>
    client.post('/auth/logout'),
}