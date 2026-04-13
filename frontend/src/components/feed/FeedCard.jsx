import { memo } from 'react'
import { Link } from 'react-router-dom'
import {
  Lightbulb, Hammer, CheckCircle2,
  MessageSquare, HandMetal,
} from 'lucide-react'
import { Avatar, Badge } from '../ui/index.js'

function timeAgo(dateString) {
  const seconds = Math.floor((Date.now() - new Date(dateString)) / 1000)
  if (seconds < 60)    return 'just now'
  if (seconds < 3600)  return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

// Event type config
const EVENT_CONFIG = {
  project_created: {
    icon:    Lightbulb,
    color:   'bg-brand-tint text-brand-primary',
    label:   (e) => 'started a new project',
    detail:  (e) => (
      <span className="flex items-center gap-2 flex-wrap">
        <Badge variant="stage" stage={e.stage} />
      </span>
    ),
  },
  milestone_posted: {
    icon:    Hammer,
    color:   'bg-green-100 text-green-700',
    label:   (e) => 'posted a milestone',
    detail:  (e) => (
      <p className="text-sm text-text-muted italic">"{e.milestone_title}"</p>
    ),
  },
  project_completed: {
    icon:    CheckCircle2,
    color:   'bg-emerald-100 text-emerald-700',
    label:   (e) => '🎉 completed a project',
    detail:  null,
  },
  comment_posted: {
    icon:    MessageSquare,
    color:   'bg-surface-offwhite text-text-muted',
    label:   (e) => 'commented on a project',
    detail:  null,
  },
  collab_request: {
    icon:    HandMetal,
    color:   'bg-purple-50 text-purple-600',
    label:   (e) => 'raised a hand to collaborate',
    detail:  null,
  },
}

export const FeedCard = memo(function FeedCard({ event }) {
  const config = EVENT_CONFIG[event.type]
  if (!config) return null

  const Icon = config.icon

  return (
    <article className="flex gap-4 p-4 bg-surface-white rounded-lg border border-ui-border hover:border-brand-border hover:shadow-sm transition-all duration-200 animate-slide-in-top">

      {/* Event icon */}
      <div className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${config.color}`}>
        <Icon className="w-4 h-4" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">

        {/* Actor + action */}
        <div className="flex items-center gap-2 flex-wrap mb-1">
          <Link
            to={`/profile/${event.owner_username ?? event.owner_id}`}
            className="flex items-center gap-1.5 hover:opacity-80 transition-opacity"
          >
            <Avatar
              src={event.owner_avatar}
              name={event.owner_display_name ?? 'Developer'}
              size="sm"
            />
            <span className="text-sm font-semibold text-text-primary">
              {event.owner_display_name ?? 'A developer'}
            </span>
          </Link>
          <span className="text-sm text-text-muted">{config.label(event)}</span>
        </div>

        {/* Project link */}
        {event.project_id && (
          <Link
            to={`/projects/${event.project_id}`}
            className="text-sm font-medium text-brand-primary hover:underline block truncate mb-1"
          >
            {event.title ?? 'View project →'}
          </Link>
        )}

        {/* Event-specific detail */}
        {config.detail && (
          <div className="mt-1">
            {config.detail(event)}
          </div>
        )}

        {/* Timestamp */}
        <time
          dateTime={event.timestamp}
          className="text-xs text-text-muted mt-1 block"
        >
          {timeAgo(event.timestamp)}
        </time>

      </div>
    </article>
  )
})