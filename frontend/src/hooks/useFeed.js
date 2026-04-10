import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore }  from '../store/authStore.js'
import { useFeedStore }  from '../store/feedStore.js'

const WS_URL                = import.meta.env.VITE_WS_URL
const RECONNECT_DELAY_MS    = 3000
const MAX_RECONNECT_ATTEMPTS = 5

export function useFeed() {
  const ws                 = useRef(null)
  const reconnectAttempts  = useRef(0)
  const reconnectTimer     = useRef(null)
  const isMounted          = useRef(true)

  const { accessToken, isAuthenticated } = useAuthStore()
  const { addEvent, setConnected, setError } = useFeedStore()

  const connect = useCallback(() => {
    if (!isAuthenticated || !accessToken) return
    if (ws.current?.readyState === WebSocket.OPEN) return

    ws.current = new WebSocket(`${WS_URL}?token=${accessToken}`)

    ws.current.onopen = () => {
      if (!isMounted.current) return
      reconnectAttempts.current = 0
      setConnected(true)
    }

    ws.current.onmessage = (event) => {
      if (!isMounted.current) return
      try {
        const data = JSON.parse(event.data)
        addEvent(data)
      } catch {
        // Malformed event — ignore silently
      }
    }

    ws.current.onclose = (event) => {
      if (!isMounted.current) return
      setConnected(false)

      // 4001 = auth failure — do not attempt reconnect
      if (event.code === 4001) {
        setError('Authentication failed. Please log in again.')
        return
      }

      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS)
      } else {
        setError('Connection lost. Please refresh the page.')
      }
    }

    ws.current.onerror = () => {
      if (!isMounted.current) return
      setError('WebSocket error — retrying...')
    }
  }, [accessToken, isAuthenticated, addEvent, setConnected, setError])

  useEffect(() => {
    isMounted.current = true
    connect()

    return () => {
      isMounted.current = false
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])

  return {
    isConnected:     useFeedStore((s) => s.isConnected),
    connectionError: useFeedStore((s) => s.connectionError),
  }
}