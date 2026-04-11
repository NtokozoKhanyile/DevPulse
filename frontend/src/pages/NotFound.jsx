import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'
import { Button } from '../components/ui/index.js'
import { Frown } from 'lucide-react'

export default function NotFound() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-screen bg-surface-offwhite flex items-center justify-center px-4">
      <div className="text-center max-w-md">

        <div className="w-20 h-20 rounded-full bg-brand-tint flex items-center justify-center mx-auto mb-6">
          <Frown className="w-10 h-10 text-brand-primary" />
        </div>

        <h1 className="text-5xl font-bold text-text-primary mb-2">404</h1>
        <h2 className="text-xl font-semibold text-text-primary mb-3">Page not found</h2>
        <p className="text-text-muted mb-8">
          This page doesn't exist or may have been moved.
        </p>

        <Link to={isAuthenticated ? '/feed' : '/'}>
          <Button size="lg">
            {isAuthenticated ? 'Back to Feed' : 'Back to Home'}
          </Button>
        </Link>

      </div>
    </div>
  )
}