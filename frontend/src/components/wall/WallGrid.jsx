import { Trophy } from 'lucide-react'
import { WallCard } from './WallCard.jsx'
import { EmptyState, Button } from '../ui/index.js'

export function WallGrid({ entries, onLoadMore, hasMore, loading }) {
  if (entries.length === 0 && !loading) {
    return (
      <EmptyState
        icon={Trophy}
        title="Wall is empty"
        description="No completed projects yet. Be the first to ship something and celebrate it here."
      />
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Masonry-style grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {entries.map((entry) => (
          <WallCard key={entry.id} entry={entry} />
        ))}
      </div>

      {/* Load more */}
      {hasMore && (
        <div className="flex justify-center">
          <Button
            variant="secondary"
            onClick={onLoadMore}
            loading={loading}
            size="lg"
          >
            Load more
          </Button>
        </div>
      )}
    </div>
  )
}