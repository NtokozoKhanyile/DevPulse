import { useEffect, useState, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Trophy, Sparkles } from 'lucide-react'
import { wallApi } from '../api/index.js'
import { Spinner } from '../components/ui/index.js'
import { WallGrid } from '../components/wall/index.js'
import { Navbar } from '../components/layout/index.js'

// Confetti burst — one-time on first load
function useConfetti() {
  const fired = useRef(false)

  useEffect(() => {
    if (fired.current) return
    fired.current = true

    const colors  = ['#1A7A3E', '#639922', '#E8F5EE', '#111111', '#ffffff']
    const count   = 80
    const container = document.body

    for (let i = 0; i < count; i++) {
      const el = document.createElement('div')
      const size = Math.random() * 8 + 4

      Object.assign(el.style, {
        position:        'fixed',
        top:             '-20px',
        left:            `${Math.random() * 100}vw`,
        width:           `${size}px`,
        height:          `${size}px`,
        borderRadius:    Math.random() > 0.5 ? '50%' : '2px',
        backgroundColor: colors[Math.floor(Math.random() * colors.length)],
        pointerEvents:   'none',
        zIndex:          9999,
        opacity:         1,
        transition:      `transform ${1.5 + Math.random()}s ease-out, opacity ${1.5 + Math.random()}s ease-out`,
      })

      container.appendChild(el)

      // Trigger animation after paint
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          Object.assign(el.style, {
            transform: `translateY(${80 + Math.random() * 40}vh) rotate(${Math.random() * 360}deg)`,
            opacity:   '0',
          })
        })
      })

      setTimeout(() => el.remove(), 3000)
    }
  }, [])
}

const LIMIT = 18

export default function CelebrationWall() {
  useConfetti()

  const [entries,  setEntries]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [page,     setPage]     = useState(1)
  const [hasMore,  setHasMore]  = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  // Initial load
  useEffect(() => {
    const fetch = async () => {
      setLoading(true)
      try {
        const { data } = await wallApi.list({ page: 1, limit: LIMIT })
        const items = data.items ?? data
        setEntries(items)
        setHasMore(items.length === LIMIT)
      } catch {
        // Silent — wall is public, show empty state gracefully
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  // Load more
  const loadMore = useCallback(async () => {
    setLoadingMore(true)
    try {
      const nextPage = page + 1
      const { data } = await wallApi.list({ page: nextPage, limit: LIMIT })
      const items = data.items ?? data
      setEntries((prev) => [...prev, ...items])
      setPage(nextPage)
      setHasMore(items.length === LIMIT)
    } catch {
      // Silent
    } finally {
      setLoadingMore(false)
    }
  }, [page])

  return (
    <div className="min-h-screen bg-surface-offwhite">

      {/* ── Hero banner ── */}
      <div className="bg-surface-dark text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">

          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-brand-primary flex items-center justify-center">
              <Trophy className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight">
              Celebration Wall
            </h1>
          </div>

          <p className="text-lg text-gray-300 max-w-xl mx-auto mb-8 leading-relaxed">
            Every project here was built in public, milestone by milestone.
            These developers shipped. Now it's their moment.
          </p>

          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-brand-primary text-white font-semibold hover:bg-green-700 transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              Start building in public
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center px-6 py-3 rounded-lg border border-white/20 text-white font-semibold hover:bg-white/10 transition-colors"
            >
              Log in
            </Link>
          </div>

        </div>
      </div>

      {/* ── Stats strip ── */}
      {entries.length > 0 && (
        <div className="bg-brand-primary text-white">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-center gap-8 text-sm">
            <div className="text-center">
              <span className="font-bold text-lg">{entries.length}+</span>
              <span className="ml-2 text-green-200">projects shipped</span>
            </div>
            <div className="w-px h-6 bg-white/20" />
            <div className="text-center">
              <span className="font-bold text-lg">
                {new Set(entries.map((e) => e.owner?.id)).size}
              </span>
              <span className="ml-2 text-green-200">developers</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Wall content ── */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <Spinner size="lg" />
          </div>
        ) : (
          <WallGrid
            entries={entries}
            onLoadMore={loadMore}
            hasMore={hasMore}
            loading={loadingMore}
          />
        )}
      </div>

    </div>
  )
}