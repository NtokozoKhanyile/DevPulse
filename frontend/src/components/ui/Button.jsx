import clsx from 'clsx'
import { Spinner } from './Spinner.jsx'

const variants = {
  primary:   'bg-brand-primary text-white hover:bg-green-800 focus-visible:ring-brand-primary',
  secondary: 'bg-brand-tint text-brand-primary border border-brand-border hover:bg-green-100',
  ghost:     'bg-transparent text-text-body hover:bg-surface-offwhite border border-ui-border',
  danger:    'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500',
  dark:      'bg-surface-dark text-white hover:bg-gray-800',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
}

export function Button({
  children,
  variant  = 'primary',
  size     = 'md',
  loading  = false,
  disabled = false,
  fullWidth = false,
  className,
  ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 font-medium rounded',
        'transition-colors duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading && <Spinner size="sm" color="inherit" />}
      {children}
    </button>
  )
}