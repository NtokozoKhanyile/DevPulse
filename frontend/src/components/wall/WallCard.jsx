import { memo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Share2, Star, Calendar } from 'lucide-react'
import { Avatar } from '../ui/index.js'
import clsx from 'clsx'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-ZA', {
    day:   'numeric',
    month: 'long',
    year:  'numeric',
  })
}

const stageCoverColors = {
  completed: 'from-green-100 to-emerald-200',
}

export const WallCard = memo(function WallCard({ entry }) {
  const {
    id,
    project,
    owner,
    shoutout,
    is_featured,
    completed_at,
  } = entry

  const [copied, setCopied] = useState(false)

  const handleShare = async (e) => {
    e.preventDefault()
    const url = `${window.location.origin}/wall`
    try {
      await navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard not available — silent
    }
  }

  return (
    <Link
      to={`/projects/${project?.id}`}
      className="group block bg-surface-white rounded-xl border border-ui-border hover:border-brand-border hover:shadow-lg transition-all duration-200"
    >
      {/* Cover */}
      <div className={clsx(
        'h-40 rounded-t-xl bg-gradient-to-br overflow-hidden relative',
        stageCoverColors.completed
      )}>
        {project?.cover_image_url && (
          <img
            src={project.cover_image_url}
            alt={`${project?.title} cover`}
            loading="lazy"
            className="w-full h-full object-cover"
          />
        )}

        {/* Featured badge */}
        {is_featured && (
          <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-400 text-yellow-900 text-xs font-bold shadow-sm">
            <Star className="w-3.5 h-3.5 fill-yellow-900" />
            Featured
          </div>
        )}

        {/* Share button */}
        <button
          onClick={handleShare}
          aria-label="Copy link to clipboard"
          className="absolute top-3 right-3 p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
        >
          {copied
            ? <span className="text-xs font-medium px-0.5">Copied!</span>
            : <Share2 className="w-3.5 h-3.5" />
          }
        </button>
      </div>

      {/* Body */}
      <div className="p-4 flex flex-col gap-3">

        {/* Title */}
        <h3 className="text-base font-bold text-text-primary group-hover:text-brand-primary transition-colors line-clamp-2 leading-snug">
          {project?.title}
        </h3>

        {/* Shoutout */}
        {shoutout && (
          <p className="text-sm text-text-body italic leading-relaxed line-clamp-3 bg-brand-tint px-3 py-2 rounded-lg border-l-2 border-brand-primary">
            "{shoutout}"
          </p>
        )}

        {/* Tech stack */}
        {project?.tech_stack?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {project.tech_stack.slice(0, 3).map((tech) => (
              <span
                key={tech}
                className="text-xs px-2 py-0.5 rounded-full bg-brand-tint text-brand-primary border border-brand-border font-medium"
              >
                {tech}
              </span>
            ))}
            {project.tech_stack.length > 3 && (
              <span className="text-xs text-text-muted self-center">
                +{project.tech_stack.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-ui-border">
          <div className="flex items-center gap-2">
            <Avatar
              src={owner?.avatar_url}
              name={owner?.display_name}
              size="sm"
            />
            <span className="text-xs font-medium text-text-muted">
              {owner?.display_name}
            </span>
          </div>
          <div className="flex items-center gap-1 text-xs text-text-muted">
            <Calendar className="w-3 h-3" />
            {formatDate(completed_at)}
          </div>
        </div>

      </div>
    </Link>
  )
})