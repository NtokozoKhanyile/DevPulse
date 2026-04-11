import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Code2, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../hooks/useAuth.js'
import { useToast, Input, Button } from '../components/ui/index.js'

export default function Login() {
  const { login }  = useAuth()
  const toast      = useToast()
  const [searchParams] = useSearchParams()
  const redirectTo = searchParams.get('redirect') ?? '/feed'

  const [showPassword, setShowPassword] = useState(false)
  const [loading,      setLoading]      = useState(false)

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm({ mode: 'onBlur' })

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await login({ email: data.email, password: data.password }, redirectTo)
      toast('Welcome back!', 'success')
    } catch (err) {
      const status = err.response?.status
      if (status === 401) {
        // Never reveal which field is wrong
        setError('email',    { message: ' ' })
        setError('password', { message: 'Invalid email or password' })
      } else {
        toast('Login failed. Please try again.', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface-offwhite flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">

        {/* Card */}
        <div className="bg-surface-white rounded-lg border border-ui-border shadow-md p-8">

          {/* Header */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-12 h-12 rounded-lg bg-brand-primary flex items-center justify-center mb-4">
              <Code2 className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary">Welcome back</h1>
            <p className="text-sm text-text-muted mt-1">Log in to your DevPulse account</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">

            <Input
              label="Email"
              type="email"
              placeholder="jane@example.com"
              required
              autoComplete="email"
              error={errors.email?.message?.trim() ? errors.email.message : undefined}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value:   /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Enter a valid email address',
                },
              })}
            />

            {/* Password with show/hide */}
            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Your password"
                required
                autoComplete="current-password"
                error={errors.password?.message}
                className="pr-10"
                {...register('password', {
                  required: 'Password is required',
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                className="absolute right-3 top-8 text-text-muted hover:text-text-primary transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            {/* Forgot password — placeholder */}
            <div className="flex justify-end -mt-2">
              <button
                type="button"
                className="text-xs text-text-muted hover:text-brand-primary transition-colors"
                onClick={() => toast('Password reset is coming soon.', 'info')}
              >
                Forgot password?
              </button>
            </div>

            <Button
              type="submit"
              fullWidth
              loading={loading}
              size="lg"
            >
              Log in
            </Button>

          </form>

          {/* Footer */}
          <p className="text-center text-sm text-text-muted mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-primary font-medium hover:underline">
              Get started free
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}