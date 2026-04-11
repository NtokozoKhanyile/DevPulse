import { Check } from 'lucide-react'
import { STAGE_ORDER } from '../../styles/theme.js'
import clsx from 'clsx'

const STAGE_LABELS = {
  idea:      'Idea',
  building:  'Building',
  testing:   'Testing',
  shipped:   'Shipped',
  completed: 'Completed',
}

export function StageSelector({ value, onChange, disabled = false }) {
  const currentIndex = STAGE_ORDER.indexOf(value)

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-text-primary">
        Project stage <span className="text-red-500 ml-0.5">*</span>
      </span>

      {/* Step track */}
      <div className="relative flex items-center">

        {/* Connecting line behind steps */}
        <div className="absolute top-5 left-5 right-5 h-0.5 bg-ui-border z-0" />

        {/* Filled portion of line */}
        <div
          className="absolute top-5 left-5 h-0.5 bg-brand-primary z-0 transition-all duration-300"
          style={{
            width: currentIndex <= 0
              ? '0%'
              : `${(currentIndex / (STAGE_ORDER.length - 1)) * 100}%`,
          }}
        />

        {/* Steps */}
        <div className="relative z-10 flex items-start justify-between w-full">
          {STAGE_ORDER.map((stage, index) => {
            const isCompleted = index < currentIndex
            const isCurrent   = index === currentIndex
            const isFuture    = index > currentIndex

            return (
              <button
                key={stage}
                type="button"
                disabled={disabled}
                onClick={() => onChange?.(stage)}
                aria-label={`Set stage to ${STAGE_LABELS[stage]}`}
                aria-pressed={isCurrent}
                className={clsx(
                  'flex flex-col items-center gap-1.5 group',
                  'disabled:cursor-not-allowed',
                  isFuture && !disabled && 'cursor-pointer'
                )}
              >
                {/* Circle */}
                <div
                  className={clsx(
                    'w-10 h-10 rounded-full border-2 flex items-center justify-center',
                    'transition-all duration-200',
                    isCompleted && 'bg-brand-primary border-brand-primary text-white',
                    isCurrent  && 'bg-brand-primary border-brand-primary text-white ring-4 ring-brand-tint',
                    isFuture   && 'bg-surface-white border-ui-border text-text-muted',
                    !disabled && isFuture && 'group-hover:border-brand-primary group-hover:text-brand-primary',
                  )}
                >
                  {isCompleted
                    ? <Check className="w-4 h-4" />
                    : <span className="text-xs font-bold">{index + 1}</span>
                  }
                </div>

                {/* Label */}
                <span
                  className={clsx(
                    'text-xs font-medium text-center leading-tight',
                    isCurrent   && 'text-brand-primary',
                    isCompleted && 'text-brand-primary',
                    isFuture    && 'text-text-muted',
                  )}
                >
                  {STAGE_LABELS[stage]}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Current stage label */}
      <p className="text-xs text-text-muted mt-1">
        Current stage: <span className="font-medium text-brand-primary capitalize">{value}</span>
      </p>
    </div>
  )
}