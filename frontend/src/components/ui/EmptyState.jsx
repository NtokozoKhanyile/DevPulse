import clsx from 'clsx'

export function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={clsx(
        'flex flex-col items-center justify-center text-center py-16 px-6',
        className
      )}
    >
      {Icon && (
        <div className="w-14 h-14 rounded-full bg-brand-tint flex items-center justify-center mb-4">
          <Icon className="w-7 h-7 text-brand-primary" />
        </div>
      )}

      <h3 className="text-base font-semibold text-text-primary mb-1">{title}</h3>

      {description && (
        <p className="text-sm text-text-muted max-w-xs mb-6">{description}</p>
      )}

      {action && action}
    </div>
  )
}