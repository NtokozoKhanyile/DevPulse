import client from './client.js'

export const wallApi = {
  list: (params = {}) =>
    client.get('/wall', { params }),

  getById: (id) =>
    client.get(`/wall/${id}`),

  // Owner of the completed project only
  updateShoutout: (id, shoutout) =>
    client.patch(`/wall/${id}/shoutout`, { shoutout }),
}