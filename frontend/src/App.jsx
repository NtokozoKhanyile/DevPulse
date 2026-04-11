import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom'
import { ToastProvider } from './components/ui/index.js'
import { Navbar }        from './components/layout/index.js'
import { useAuthStore }  from './store/authStore.js'

import Landing          from './pages/Landing.jsx'
import Login            from './pages/Login.jsx'
import Register         from './pages/Register.jsx'
import Feed             from './pages/Feed.jsx'
import ProjectDetail    from './pages/ProjectDetail.jsx'
import NewProject       from './pages/NewProject.jsx'
import EditProject      from './pages/EditProject.jsx'
import Profile          from './pages/Profile.jsx'
import CelebrationWall  from './pages/CelebrationWall.jsx'
import NotFound         from './pages/NotFound.jsx'

// Protected route guard
function ProtectedRoute() {
  const { isAuthenticated } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated) {
    return (
      <Navigate
        to={`/login?redirect=${encodeURIComponent(location.pathname)}`}
        replace
      />
    )
  }

  return <Outlet />
}

// App shell
function AppShell() {
  return (
    <div className="min-h-screen flex flex-col bg-surface-offwhite">
      <Navbar />
      <Routes>
        {/* Public */}
        <Route path="/"                      element={<Landing />} />
        <Route path="/login"                 element={<Login />} />
        <Route path="/register"              element={<Register />} />
        <Route path="/wall"                  element={<CelebrationWall />} />
        <Route path="/profile/:username"     element={<Profile />} />
        <Route path="/projects/:id"          element={<ProjectDetail />} />

        {/* Protected */}
        <Route element={<ProtectedRoute />}>
          <Route path="/feed"                element={<Feed />} />
          <Route path="/projects/new"        element={<NewProject />} />
          <Route path="/projects/:id/edit"   element={<EditProject />} />
          <Route path="/profile/me"          element={<Profile />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

// Root
export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AppShell />
      </ToastProvider>
    </BrowserRouter>
  )
}