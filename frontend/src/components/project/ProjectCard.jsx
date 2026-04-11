import { memo } from 'react'
import { Link } from 'react-router-dom'
import { Eye, Calendar } from 'lucide-react'
import { Avatar, Badge } from '../ui/index.js'
import clsx from 'clsx'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-ZA', {
    day:   'numeric',
    month: 'short',
    year:  'numeric',
  })
}

// Stage gradient placeholders when no cover image
const stagGradients = {
  idea:      'from-gray-100 to-gray-200',
  building:  'from-brand-tint to-green-200',
  testing:   'from-orange-50 to-orange-100',
  shipped:   'from-blue-50 to-blue-100',
  completed: 'from-green-100 to-green-200',
}

export const ProjectCard = memo(function ProjectCard({ project }) {
  const {
    id, title, description, stage,
    tech_stack = [], support_tags = [],
    cover_image_url, owner, view_count, created_at,
  } = project

  return (
    <Link
      to={`/projects/${id}`}
      className="group block bg-surface-white rounded-lg border border-ui-border hover:border-brand-border hover:shadow-md transition-all duration-200"
    >
      {/* Cover */}
      <div className={clsx(
        'h-36 rounded-t-lg bg-gradient-to-br overflow-hidden',
        stagGradients[stage] ?? stagGradients.idea
      )}>
        {cover_image_url && (
          <img
            src={cover_image_url}
            alt={`${title} cover`}
            loading="lazy"
            className="w-full h-full object-cover"
          />
        )}
      </div>

      {/* Body */}
      <div className="p-4 flex flex-col gap-3">

        {/* Title + stage */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-base font-semibold text-text-primary leading-snug group-hover:text-brand-primary transition-colors line-clamp-2">
            {title}
          </h3>
          <Badge variant="stage" stage={stage} className="shrink-0 mt-0.5" />
        </div>

        {/* Description */}
        {description && (
          <p className="text-sm text-text-body line-clamp-2 leading-relaxed">
            {description}
          </p>
        )}

        {/* Tech stack */}
        {tech_stack.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tech_stack.slice(0, 4).map((tech) => (
              <Badge key={tech} label={tech} variant="tag" />
            ))}
            {tech_stack.length > 4 && (
              <span className="text-xs text-text-muted self-center">
                +{tech_stack.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Support tags */}
        {support_tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {support_tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded-full bg-surface-offwhite text-text-muted border border-ui-border"
              >
                needs {tag}
              </span>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-1 border-t border-ui-border">
          {/* Owner */}
          <div className="flex items-center gap-2">
            <Avatar
              src={owner?.avatar_url}
              name={owner?.display_name}
              size="sm"
            />
            <span className="text-xs text-text-muted font-medium">
              {owner?.display_name}
            </span>
          </div>

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-text-muted">
            <span className="flex items-center gap-1">
              <Eye className="w-3.5 h-3.5" />
              {view_count ?? 0}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {formatDate(created_at)}
            </span>
          </div>
        </div>

      </div>
    </Link>
  )
})