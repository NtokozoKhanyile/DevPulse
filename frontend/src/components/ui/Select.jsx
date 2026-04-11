import { forwardRef } from 'react'
import clsx from 'clsx'

export const Select = forwardRef(function Select(
  { label, error, options = [], placeholder, className, id, required, ...props },
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

      <select
        ref={ref}
        id={inputId}
        className={clsx(
          'w-full px-3 py-2 rounded border text-sm text-text-primary',
          'bg-surface-white',
          'transition-colors duration-150',
          'focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent',
          error ? 'border-red-500' : 'border-ui-border hover:border-gray-400',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
        aria-invalid={!!error}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      {error && (
        <p className="text-xs text-red-500" role="alert">{error}</p>
      )}
    </div>
  )
})