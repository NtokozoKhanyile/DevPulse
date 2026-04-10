import { create } from 'zustand'

export const useFeedStore = create((set) => ({
  events:          [],   // capped at 100 — see addEvent
  isConnected:     false,
  connectionError: null,

  addEvent: (event) =>
    set((state) => ({
      events: [event, ...state.events].slice(0, 100),
    })),

  // Bulk load from HTTP fallback on initial mount
  loadEvents: (events) =>
    set({ events: events.slice(0, 100) }),

  setConnected: (isConnected) =>
    set({ isConnected, connectionError: null }),

  setError: (error) =>
    set({ connectionError: error, isConnected: false }),

  clearFeed: () =>
    set({ events: [] }),
}))