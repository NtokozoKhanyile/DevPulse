import { memo } from 'react'
import { FeedCard } from './FeedCard.jsx'
import { EmptyState } from '../ui/index.js'
import { Radio } from 'lucide-react'

export const FeedList = memo(function FeedList({ events }) {
  if (events.length === 0) {
    return (
      <EmptyState
        icon={Radio}
        title="Feed is quiet"
        description="No activity yet. Create a project or wait for other developers to build in public."
      />
    )
  }

  return (
    <section
      aria-live="polite"
      aria-label="Live developer feed"
      className="flex flex-col gap-3"
    >
      {events.map((event, index) => (
        <FeedCard key={`${event.type}-${event.timestamp}-${index}`} event={event} />
      ))}
    </section>
  )
})