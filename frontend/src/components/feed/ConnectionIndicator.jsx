import clsx from 'clsx'

export function ConnectionIndicator({ isConnected, error }) {
  if (error) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-50 border border-red-200">
        <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
        <span className="text-xs font-medium text-red-700">Disconnected</span>
      </div>
    )
  }

  return (
    <div className={clsx(
      'flex items-center gap-2 px-3 py-1.5 rounded-full border transition-colors duration-300',
      isConnected
        ? 'bg-brand-tint border-brand-border'
        : 'bg-yellow-50 border-yellow-200'
    )}>
      <span className={clsx(
        'w-2 h-2 rounded-full shrink-0',
        isConnected
          ? 'bg-brand-primary animate-pulse'
          : 'bg-yellow-500 animate-pulse'
      )} />
      <span className={clsx(
        'text-xs font-medium',
        isConnected ? 'text-brand-primary' : 'text-yellow-700'
      )}>
        {isConnected ? 'Live' : 'Reconnecting…'}
      </span>
    </div>
  )
}