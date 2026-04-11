import clsx from 'clsx'
import { stageColors } from '../../styles/theme.js'

export function Badge({ label, variant = 'stage', stage, className }) {
  if (variant === 'stage' && stage) {
    const colors = stageColors[stage] ?? stageColors.idea
    return (
      <span
        className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border', className)}
        style={{ backgroundColor: colors.bg, color: colors.text, borderColor: colors.border }}
      >
        {label ?? stage.charAt(0).toUpperCase() + stage.slice(1)}
      </span>
    )
  }

  // Support tags and tech stack tags
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        'bg-brand-tint text-brand-primary border border-brand-border',
        className
      )}
    >
      {label}
    </span>
  )
}