import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Bell, Code2, LogOut, Plus, User } from 'lucide-react'
import { useAuthStore } from '../../store/authStore.js'
import { useNotificationStore } from '../../store/notificationStore.js'
import { useAuth } from '../../hooks/useAuth.js'
import { Avatar } from '../ui/index.js'
import clsx from 'clsx'

export function Navbar() {
  const { isAuthenticated, user } = useAuthStore()
  const unreadCount = useNotificationStore((s) => s.unreadCount)
  const { logout } = useAuth()
  const navigate = useNavigate()

  const navLinkClass = ({ isActive }) =>
    clsx(
      'text-sm font-medium transition-colors duration-150 px-3 py-2 rounded',
      isActive
        ? 'text-brand-primary bg-brand-tint'
        : 'text-gray-300 hover:text-white hover:bg-white/10'
    )

  return (
    <header className="bg-surface-dark border-b border-white/10 sticky top-0 z-40">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link
            to={isAuthenticated ? '/feed' : '/'}
            className="flex items-center gap-2 text-white hover:opacity-90 transition-opacity"
          >
            <div className="w-8 h-8 rounded bg-brand-primary flex items-center justify-center shrink-0">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">DevPulse</span>
          </Link>

          {/* Centre nav — authenticated only */}
          {isAuthenticated && (
            <div className="hidden md:flex items-center gap-1">
              <NavLink to="/feed"         className={navLinkClass}>Feed</NavLink>
              <NavLink to="/wall"         className={navLinkClass}>Wall</NavLink>
              <NavLink to="/projects/new" className={navLinkClass}>
                <span className="flex items-center gap-1">
                  <Plus className="w-4 h-4" />New Project
                </span>
              </NavLink>
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <>
                {/* Notification bell */}
                <button
                  onClick={() => navigate('/profile/me')}
                  aria-label={`Notifications — ${unreadCount} unread`}
                  className="relative p-2 rounded text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-4 h-4 bg-brand-primary rounded-full text-white text-[10px] font-bold flex items-center justify-center">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Profile */}
                <button
                  onClick={() => navigate('/profile/me')}
                  aria-label="Go to your profile"
                  className="flex items-center gap-2 p-1.5 rounded hover:bg-white/10 transition-colors"
                >
                  <Avatar
                    src={user?.avatar_url}
                    name={user?.display_name}
                    size="sm"
                  />
                  <span className="hidden md:block text-sm font-medium text-gray-200">
                    {user?.display_name}
                  </span>
                </button>

                {/* Logout */}
                <button
                  onClick={logout}
                  aria-label="Log out"
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-gray-300 hover:text-white px-3 py-2 rounded transition-colors"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="text-sm font-medium bg-brand-primary text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
                >
                  Get started
                </Link>
              </>
            )}
          </div>

        </div>
      </nav>
    </header>
  )
}