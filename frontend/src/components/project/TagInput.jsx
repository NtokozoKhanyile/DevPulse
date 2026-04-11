import { useState, useRef } from 'react'
import { X } from 'lucide-react'
import clsx from 'clsx'

export function TagInput({ label, value = [], onChange, placeholder, hint, max = 10 }) {
  const [input,   setInput]   = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef(null)

  const addTag = (raw) => {
    const tag = raw.trim().toLowerCase().replace(/\s+/g, '-')
    if (!tag || value.includes(tag) || value.length >= max) return
    onChange([...value, tag])
    setInput('')
  }

  const removeTag = (tag) => {
    onChange(value.filter((t) => t !== tag))
  }

  const handleKeyDown = (e) => {
    if (['Enter', ',', 'Tab'].includes(e.key)) {
      e.preventDefault()
      addTag(input)
    }
    if (e.key === 'Backspace' && !input && value.length > 0) {
      removeTag(value[value.length - 1])
    }
  }

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-text-primary">
          {label}
        </label>
      )}

      <div
        onClick={() => inputRef.current?.focus()}
        className={clsx(
          'flex flex-wrap gap-1.5 min-h-[42px] px-3 py-2 rounded border bg-surface-white cursor-text',
          'transition-colors duration-150',
          focused
            ? 'border-brand-primary ring-2 ring-brand-primary ring-offset-0'
            : 'border-ui-border hover:border-gray-400'
        )}
      >
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-brand-tint text-brand-primary border border-brand-border"
          >
            {tag}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); removeTag(tag) }}
              aria-label={`Remove ${tag}`}
              className="hover:text-red-500 transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}

        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => { setFocused(false); addTag(input) }}
          placeholder={value.length === 0 ? placeholder : ''}
          className="flex-1 min-w-[120px] text-sm text-text-primary bg-transparent outline-none placeholder:text-text-muted"
          aria-label={label}
        />
      </div>

      {hint && (
        <p className="text-xs text-text-muted">{hint}</p>
      )}

      {value.length >= max && (
        <p className="text-xs text-text-muted">Maximum {max} tags reached</p>
      )}
    </div>
  )
}