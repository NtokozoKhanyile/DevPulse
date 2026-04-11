import { Link } from 'react-router-dom'
import { Trophy, Tag } from 'lucide-react'
import { useNotificationStore } from '../../store/notificationStore.js'
import { useAuthStore } from '../../store/authStore.js'
import { notificationsApi } from '../../api/index.js'
import { useEffect } from 'react'
import { Badge } from '../ui/index.js'

const SUPPORT_TAGS = [
  'code-review', 'design', 'testing', 'backend',
  'frontend', 'devops', 'mentorship', 'funding',
]

export function Sidebar() {
  const { isAuthenticated } = useAuthStore()
  const { notifications, setNotifications, setUnreadCount } =
    useNotificationStore()

  // Poll unread count every 30 seconds
  useEffect(() => {
    if (!isAuthenticated) return

    const fetchCount = async () => {
      try {
        const { data } = await notificationsApi.getUnreadCount()
        setUnreadCount(data.count)
      } catch {
        // Silent — sidebar is non-critical
      }
    }

    fetchCount()
    const interval = setInterval(fetchCount, 30_000)
    return () => clearInterval(interval)
  }, [isAuthenticated, setUnreadCount])

  // Fetch recent notifications for display
  useEffect(() => {
    if (!isAuthenticated) return

    const fetchNotifications = async () => {
      try {
        const { data } = await notificationsApi.list({ limit: 5 })
        setNotifications(data.items ?? data)
      } catch {
        // Silent
      }
    }

    fetchNotifications()
  }, [isAuthenticated, setNotifications])

  return (
    <aside className="w-72 shrink-0 hidden lg:flex flex-col gap-6">

      {/* Celebration Wall CTA */}
      <div className="bg-surface-dark rounded-lg p-5 text-white">
        <div className="flex items-center gap-2 mb-2">
          <Trophy className="w-5 h-5 text-brand-accent" />
          <span className="font-semibold text-sm">Celebration Wall</span>
        </div>
        <p className="text-xs text-gray-400 mb-4 leading-relaxed">
          See what developers have shipped and completed. Be inspired.
        </p>
        <Link
          to="/wall"
          className="block w-full text-center text-sm font-medium bg-brand-primary text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
        >
          View the Wall
        </Link>
      </div>

      {/* Trending support tags */}
      <div className="bg-surface-white rounded-lg border border-ui-border p-5">
        <div className="flex items-center gap-2 mb-4">
          <Tag className="w-4 h-4 text-brand-primary" />
          <span className="font-semibold text-sm text-text-primary">Support needed</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {SUPPORT_TAGS.map((tag) => (
            <Badge key={tag} label={tag} variant="tag" />
          ))}
        </div>
      </div>

      {/* Recent notifications */}
      {isAuthenticated && notifications.length > 0 && (
        <div className="bg-surface-white rounded-lg border border-ui-border p-5">
          <span className="font-semibold text-sm text-text-primary block mb-3">
            Recent notifications
          </span>
          <ul className="flex flex-col gap-3">
            {notifications.slice(0, 5).map((n) => (
              <li key={n.id} className="flex items-start gap-2">
                <span
                  className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                    n.is_read ? 'bg-ui-border' : 'bg-brand-primary'
                  }`}
                />
                <p className="text-xs text-text-body leading-snug">{n.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

    </aside>
  )
}