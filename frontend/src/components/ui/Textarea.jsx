import { forwardRef } from 'react'
import clsx from 'clsx'

export const Textarea = forwardRef(function Textarea(
  { label, error, hint, className, id, required, rows = 4, ...props },
  ref
) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-text-primary"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <textarea
        ref={ref}
        id={inputId}
        rows={rows}
        className={clsx(
          'w-full px-3 py-2 rounded border text-sm text-text-primary',
          'bg-surface-white placeholder:text-text-muted resize-y',
          'transition-colors duration-150',
          'focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent',
          error
            ? 'border-red-500 focus:ring-red-400'
            : 'border-ui-border hover:border-gray-400',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />

      {hint && !error && (
        <p className="text-xs text-text-muted">{hint}</p>
      )}

      {error && (
        <p id={`${inputId}-error`} className="text-xs text-red-500" role="alert">
          {error}
        </p>
      )}
    </div>
  )
})