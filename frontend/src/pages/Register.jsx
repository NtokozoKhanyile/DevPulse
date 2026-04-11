import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Code2, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../hooks/useAuth.js'
import { useToast } from '../components/ui/index.js'
import { Input, Button } from '../components/ui/index.js'

// Password strength
function getPasswordStrength(password = '') {
  let score = 0
  if (password.length >= 8)                    score++
  if (password.length >= 12)                   score++
  if (/[A-Z]/.test(password))                  score++
  if (/[0-9]/.test(password))                  score++
  if (/[^A-Za-z0-9]/.test(password))           score++

  if (score <= 1) return { label: 'Weak',   color: 'bg-red-500',    width: 'w-1/4' }
  if (score <= 2) return { label: 'Fair',   color: 'bg-yellow-500', width: 'w-2/4' }
  if (score <= 3) return { label: 'Good',   color: 'bg-brand-accent', width: 'w-3/4' }
  return           { label: 'Strong', color: 'bg-brand-primary', width: 'w-full' }
}

function PasswordStrengthBar({ password }) {
  if (!password) return null
  const { label, color, width } = getPasswordStrength(password)

  return (
    <div className="mt-1">
      <div className="h-1.5 w-full bg-ui-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${color} ${width}`}
        />
      </div>
      <p className="text-xs text-text-muted mt-1">
        Password strength: <span className="font-medium">{label}</span>
      </p>
    </div>
  )
}

// Page
export default function Register() {
  const { register: registerUser } = useAuth()
  const toast    = useToast()
  const navigate = useNavigate()

  const [showPassword, setShowPassword] = useState(false)
  const [loading,      setLoading]      = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setError,
    formState: { errors },
  } = useForm({ mode: 'onBlur' })

  const passwordValue = watch('password', '')

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await registerUser({
        username:     data.username,
        email:        data.email,
        password:     data.password,
        display_name: data.display_name,
      })
      toast('Welcome to DevPulse! 🎉', 'success')
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail ?? ''

      if (status === 409) {
        if (detail.toLowerCase().includes('username')) {
          setError('username', { message: 'Username already taken' })
        } else if (detail.toLowerCase().includes('email')) {
          setError('email', { message: 'Email already registered' })
        } else {
          setError('username', { message: 'Username or email already taken' })
        }
      } else {
        toast('Registration failed. Please try again.', 'error')
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
            <h1 className="text-2xl font-bold text-text-primary">Create your account</h1>
            <p className="text-sm text-text-muted mt-1">Build in public. Ship with confidence.</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">

            <Input
              label="Display name"
              placeholder="Jane Doe"
              required
              error={errors.display_name?.message}
              {...register('display_name', {
                required: 'Display name is required',
                minLength: { value: 2, message: 'At least 2 characters' },
                maxLength: { value: 100, message: 'Max 100 characters' },
              })}
            />

            <Input
              label="Username"
              placeholder="janedoe"
              required
              hint="3–50 characters. Letters, numbers, underscores only."
              error={errors.username?.message}
              {...register('username', {
                required: 'Username is required',
                minLength: { value: 3,  message: 'At least 3 characters' },
                maxLength: { value: 50, message: 'Max 50 characters' },
                pattern: {
                  value:   /^[a-z0-9_]+$/,
                  message: 'Lowercase letters, numbers, and underscores only',
                },
              })}
            />

            <Input
              label="Email"
              type="email"
              placeholder="jane@example.com"
              required
              error={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value:   /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Enter a valid email address',
                },
              })}
            />

            {/* Password with show/hide toggle */}
            <div className="flex flex-col gap-1">
              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Min. 8 characters"
                  required
                  error={errors.password?.message}
                  className="pr-10"
                  {...register('password', {
                    required:  'Password is required',
                    minLength: { value: 8, message: 'At least 8 characters required' },
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
              <PasswordStrengthBar password={passwordValue} />
            </div>

            <Button
              type="submit"
              fullWidth
              loading={loading}
              size="lg"
              className="mt-2"
            >
              Create account
            </Button>

          </form>

          {/* Footer */}
          <p className="text-center text-sm text-text-muted mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-primary font-medium hover:underline">
              Log in
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}