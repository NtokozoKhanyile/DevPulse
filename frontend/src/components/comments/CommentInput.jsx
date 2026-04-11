import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '../../store/authStore.js'
import { Avatar, Button } from '../ui/index.js'
import clsx from 'clsx'

export function CommentInput({ onSubmit, placeholder = 'Leave a comment...', compact = false }) {
  const { user, isAuthenticated } = useAuthStore()
  const [loading, setLoading]     = useState(false)
  const [focused, setFocused]     = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  if (!isAuthenticated) return null

  const submit = async (data) => {
    setLoading(true)
    try {
      await onSubmit(data.body)
      reset()
      setFocused(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex gap-3 items-start">
        <Avatar
          src={user?.avatar_url}
          name={user?.display_name}
          size={compact ? 'sm' : 'md'}
          className="shrink-0 mt-1"
        />

        <div className="flex-1 flex flex-col gap-2">
          <textarea
            placeholder={placeholder}
            onFocus={() => setFocused(true)}
            rows={focused ? 3 : 1}
            aria-label="Comment text"
            aria-invalid={!!errors.body}
            className={clsx(
              'w-full px-3 py-2 rounded border text-sm text-text-primary',
              'bg-surface-white placeholder:text-text-muted resize-none',
              'transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent',
              errors.body ? 'border-red-500' : 'border-ui-border hover:border-gray-400'
            )}
            {...register('body', {
              required:  'Comment cannot be empty',
              maxLength: { value: 2000, message: 'Max 2000 characters' },
            })}
          />

          {errors.body && (
            <p className="text-xs text-red-500" role="alert">{errors.body.message}</p>
          )}

          {focused && (
            <div className="flex gap-2 justify-end animate-fade-in">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => { reset(); setFocused(false) }}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" size="sm" loading={loading}>
                Comment
              </Button>
            </div>
          )}
        </div>
      </div>
    </form>
  )
}