import { memo } from 'react'
import { CheckCircle2 } from 'lucide-react'
import { EmptyState } from '../ui/index.js'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-ZA', {
    day:   'numeric',
    month: 'short',
    year:  'numeric',
  })
}

const MilestoneItem = memo(function MilestoneItem({ milestone, isLast }) {
  return (
    <li className="relative flex gap-4">
      {/* Vertical line — hidden on last item */}
      {!isLast && (
        <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-brand-border" />
      )}

      {/* Icon */}
      <div className="shrink-0 w-8 h-8 rounded-full bg-brand-primary flex items-center justify-center mt-1 z-10">
        <CheckCircle2 className="w-4 h-4 text-white" />
      </div>

      {/* Content */}
      <div className="flex-1 pb-8">
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-semibold text-text-primary leading-snug">
            {milestone.title}
          </h4>
          <time
            dateTime={milestone.created_at}
            className="text-xs text-text-muted shrink-0 mt-0.5"
          >
            {formatDate(milestone.created_at)}
          </time>
        </div>

        {milestone.body && (
          <p className="text-sm text-text-body mt-1 leading-relaxed">
            {milestone.body}
          </p>
        )}
      </div>
    </li>
  )
})

export function MilestoneList({ milestones = [] }) {
  if (milestones.length === 0) {
    return (
      <EmptyState
        title="No milestones yet"
        description="Progress updates will appear here as the project moves forward."
      />
    )
  }

  return (
    <ul className="flex flex-col" aria-label="Project milestones">
      {milestones.map((milestone, index) => (
        <MilestoneItem
          key={milestone.id}
          milestone={milestone}
          isLast={index === milestones.length - 1}
        />
      ))}
    </ul>
  )
}