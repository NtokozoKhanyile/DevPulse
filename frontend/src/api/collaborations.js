import client from './client.js'

export const collaborationsApi = {
  // message is optional
  raiseHand: (projectId, message = '') =>
    client.post(`/projects/${projectId}/collaborate`, { message }),

  // Owner only — list all requests for their project
  list: (projectId) =>
    client.get(`/projects/${projectId}/collaborate`),

  // status: 'accepted' | 'declined'
  respond: (projectId, requestId, status) =>
    client.patch(`/projects/${projectId}/collaborate/${requestId}`, { status }),
}