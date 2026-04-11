import clsx from 'clsx'

const sizes = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-14 h-14 text-lg',
  xl: 'w-20 h-20 text-2xl',
}

function getInitials(name = '') {
  return name
    .trim()
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

export function Avatar({ src, name, size = 'md', className }) {
  const initials = getInitials(name)

  if (src) {
    return (
      <img
        src={src}
        alt={name ? `${name}'s avatar` : 'User avatar'}
        loading="lazy"
        className={clsx(
          'rounded-full object-cover shrink-0',
          sizes[size],
          className
        )}
      />
    )
  }

  return (
    <div
      aria-label={name ? `${name}'s avatar` : 'User avatar'}
      className={clsx(
        'rounded-full shrink-0 flex items-center justify-center',
        'bg-brand-primary text-white font-semibold select-none',
        sizes[size],
        className
      )}
    >
      {initials || '?'}
    </div>
  )
}