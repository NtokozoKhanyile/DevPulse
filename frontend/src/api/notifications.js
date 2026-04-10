import client from './client.js'

export const notificationsApi = {
  list: (params = {}) =>
    client.get('/notifications', { params }),

  markRead: (id) =>
    client.patch(`/notifications/${id}/read`),

  markAllRead: () =>
    client.patch('/notifications/read-all'),

  getUnreadCount: () =>
    client.get('/notifications/unread-count'),
}