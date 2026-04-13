import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Code2, Zap, Users, Trophy,
  ArrowRight, Radio, GitCommit, Star,
} from 'lucide-react'
import { wallApi, projectsApi } from '../api/index.js'
import { Spinner, Avatar, Badge } from '../components/ui/index.js'
import { WallCard } from '../components/wall/index.js'

// ── Stat card ─────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, value, label }) {
  return (
    <div className="flex flex-col items-center gap-2 p-6 bg-surface-white rounded-xl border border-ui-border">
      <div className="w-10 h-10 rounded-full bg-brand-tint flex items-center justify-center">
        <Icon className="w-5 h-5 text-brand-primary" />
      </div>
      <p className="text-3xl font-bold text-text-primary">{value}</p>
      <p className="text-sm text-text-muted">{label}</p>
    </div>
  )
}

// ── Feature card ──────────────────────────────────────────────────────────
function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="p-6 bg-surface-white rounded-xl border border-ui-border hover:border-brand-border hover:shadow-md transition-all duration-200">
      <div className="w-10 h-10 rounded-lg bg-brand-tint flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-brand-primary" />
      </div>
      <h3 className="text-base font-bold text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-muted leading-relaxed">{description}</p>
    </div>
  )
}

export default function Landing() {
  const [wallEntries,    setWallEntries]    = useState([])
  const [stats,          setStats]          = useState(null)
  const [loadingWall,    setLoadingWall]    = useState(true)
  const [loadingStats,   setLoadingStats]   = useState(true)

  // ── Fetch wall preview ─────────────────────────────────────────────────
  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await wallApi.list({ limit: 3 })
        setWallEntries(data.items ?? data)
      } catch {
        // Non-critical — show section with empty state
      } finally {
        setLoadingWall(false)
      }
    }
    fetch()
  }, [])

  // ── Derive stats from project list ─────────────────────────────────────
  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await projectsApi.list({ limit: 1 })
        // Use total from paginated response if available
        setStats({
          projects: data.total ?? data.length ?? '—',
        })
      } catch {
        setStats(null)
      } finally {
        setLoadingStats(false)
      }
    }
    fetch()
  }, [])

  return (
    <div className="min-h-screen bg-surface-offwhite">

      {/* ── Hero ── */}
      <section className="bg-surface-dark text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">

          {/* Logo mark */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="w-14 h-14 rounded-xl bg-brand-primary flex items-center justify-center shadow-lg">
              <Code2 className="w-8 h-8 text-white" />
            </div>
            <span className="text-4xl font-black tracking-tight">DevPulse</span>
          </div>

          <h1 className="text-5xl sm:text-6xl font-black leading-tight tracking-tight mb-6 text-balance">
            Build in public.{' '}
            <span className="text-brand-accent">Ship with confidence.</span>
          </h1>

          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            DevPulse is where developers share what they're building, track milestones,
            find collaborators, and celebrate shipping. All in real time.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-lg bg-brand-primary text-white font-bold text-lg hover:bg-green-700 transition-colors shadow-lg"
            >
              Get started free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/wall"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-lg border border-white/20 text-white font-bold text-lg hover:bg-white/10 transition-colors"
            >
              <Trophy className="w-5 h-5" />
              See the Wall
            </Link>
          </div>

        </div>
      </section>

      {/* ── Live indicator strip ── */}
      <div className="bg-brand-primary text-white">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-center gap-2 text-sm font-medium">
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          Developers are building in public right now
        </div>
      </div>

      {/* ── Stats ── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {loadingStats ? (
            <div className="sm:col-span-3 flex justify-center py-8">
              <Spinner />
            </div>
          ) : (
            <>
              <StatCard
                icon={GitCommit}
                value={stats?.projects ?? '—'}
                label="Projects in progress"
              />
              <StatCard
                icon={Radio}
                value="Live"
                label="Real-time feed"
              />
              <StatCard
                icon={Trophy}
                value={wallEntries.length > 0 ? `${wallEntries.length}+` : '—'}
                label="Projects shipped"
              />
            </>
          )}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-text-primary mb-3">
            Everything you need to build in public
          </h2>
          <p className="text-text-muted max-w-xl mx-auto">
            From first idea to shipped product. Track it, share it, celebrate it.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <FeatureCard
            icon={Code2}
            title="Project entries"
            description="Log what you're building with stage, tech stack, and what support you need."
          />
          <FeatureCard
            icon={Radio}
            title="Live feed"
            description="See what other developers are building in real time via WebSocket."
          />
          <FeatureCard
            icon={Users}
            title="Collaboration"
            description="Raise your hand on projects you want to join. Accept collaborators on yours."
          />
          <FeatureCard
            icon={Trophy}
            title="Celebration Wall"
            description="Ship a project and get added to the public wall of builders. You earned it."
          />
        </div>
      </section>

      {/* ── Wall preview ── */}
      <section className="bg-surface-dark text-white py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-bold mb-1">Recently shipped</h2>
              <p className="text-gray-400 text-sm">Projects that made it to the Celebration Wall</p>
            </div>
            <Link
              to="/wall"
              className="flex items-center gap-2 text-brand-accent hover:text-green-400 font-semibold text-sm transition-colors"
            >
              View full wall <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loadingWall ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : wallEntries.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {wallEntries.map((entry) => (
                <WallCard key={entry.id} entry={entry} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Trophy className="w-10 h-10 mx-auto mb-3 opacity-40" />
              <p>No shipped projects yet. Be the first.</p>
            </div>
          )}

        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-4xl font-black text-text-primary mb-4">
          Ready to build in public?
        </h2>
        <p className="text-text-muted text-lg mb-8 max-w-lg mx-auto">
          Join developers who are shipping in the open, learning together,
          and celebrating every milestone.
        </p>
        <Link
          to="/register"
          className="inline-flex items-center gap-2 px-10 py-4 rounded-lg bg-brand-primary text-white font-bold text-lg hover:bg-green-700 transition-colors shadow-lg"
        >
          Create your account
          <ArrowRight className="w-5 h-5" />
        </Link>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-surface-dark text-gray-400 py-8">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-brand-primary flex items-center justify-center">
              <Code2 className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white">DevPulse</span>
          </div>
          <p className="text-xs">
            Built in public. Shipped with confidence.
          </p>
          <div className="flex gap-4 text-sm">
            <Link to="/wall"     className="hover:text-white transition-colors">Wall</Link>
            <Link to="/register" className="hover:text-white transition-colors">Register</Link>
            <Link to="/login"    className="hover:text-white transition-colors">Login</Link>
          </div>
        </div>
      </footer>

    </div>
  )
}