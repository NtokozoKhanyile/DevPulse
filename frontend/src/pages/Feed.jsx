import { useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'
import { useFeed }      from '../hooks/useFeed.js'
import { useFeedStore } from '../store/feedStore.js'
import { projectsApi }  from '../api/index.js'
import { useToast, Button, Spinner } from '../components/ui/index.js'
import { Sidebar }      from '../components/layout/index.js'
import { FeedList, ConnectionIndicator } from '../components/feed/index.js'
import { useState } from 'react'

export default function Feed() {
  const toast   = useToast()
  const { isConnected, connectionError } = useFeed()
  const { events, loadEvents }           = useFeedStore()

  const [httpLoading,  setHttpLoading]  = useState(false)
  const [httpLoaded,   setHttpLoaded]   = useState(false)
  const hasFetchedRef = useRef(false)

  // ── HTTP fallback — populate feed before WS delivers events ──────────
  const loadHttpFallback = useCallback(async () => {
    if (hasFetchedRef.current) return
    hasFetchedRef.current = true
    setHttpLoading(true)

    try {
      const { data } = await projectsApi.list({ limit: 20 })
      const items = data.items ?? data

      // Shape project list items into feed-compatible event objects
      const shaped = items.map((project) => ({
        type:                'project_created',
        project_id:          project.id,
        title:               project.title,
        stage:               project.stage,
        owner_id:            project.owner_id,
        owner_display_name:  project.owner?.display_name,
        owner_username:      project.owner?.username,
        owner_avatar:        project.owner?.avatar_url,
        timestamp:           project.created_at,
      }))

      loadEvents(shaped)
      setHttpLoaded(true)
    } catch {
      toast('Could not load feed. Please refresh.', 'error')
    } finally {
      setHttpLoading(false)
    }
  }, [loadEvents, toast])

  useEffect(() => {
    loadHttpFallback()
  }, [loadHttpFallback])

  // ── Manual refresh ────────────────────────────────────────────────────
  const handleRefresh = async () => {
    hasFetchedRef.current = false
    setHttpLoaded(false)
    await loadHttpFallback()
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex gap-8 items-start">

        {/* ── Main feed column ── */}
        <div className="flex-1 min-w-0">

          {/* Feed header */}
          <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-text-primary">Developer Feed</h1>
              <ConnectionIndicator
                isConnected={isConnected}
                error={connectionError}
              />
            </div>

            <div className="flex items-center gap-2">
              {/* Refresh button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRefresh}
                disabled={httpLoading}
                aria-label="Refresh feed"
              >
                <RefreshCw className={`w-4 h-4 ${httpLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>

              {/* New project CTA */}
              <Link to="/projects/new">
                <Button size="sm">
                  <Plus className="w-4 h-4" />
                  New project
                </Button>
              </Link>
            </div>
          </div>

          {/* Event count */}
          {events.length > 0 && (
            <p className="text-xs text-text-muted mb-4">
              Showing {events.length} {events.length === 1 ? 'event' : 'events'}
              {events.length === 100 && ' (max 100 — oldest events removed)'}
            </p>
          )}

          {/* Connection error banner */}
          {connectionError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between gap-4">
              <p className="text-sm text-red-700">{connectionError}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.reload()}
              >
                Refresh page
              </Button>
            </div>
          )}

          {/* Loading state */}
          {httpLoading && events.length === 0 ? (
            <div className="flex items-center justify-center py-20">
              <Spinner size="lg" />
            </div>
          ) : (
            <FeedList events={events} />
          )}

        </div>

        {/* ── Sidebar ── */}
        <Sidebar />

      </div>
    </div>
  )
}