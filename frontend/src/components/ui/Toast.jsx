import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { CheckCircle, XCircle, Info, X } from 'lucide-react'
import clsx from 'clsx'

// Context
const ToastContext = createContext(null)

const icons = {
  success: <CheckCircle className="w-5 h-5 text-brand-primary shrink-0" />,
  error:   <XCircle    className="w-5 h-5 text-red-500 shrink-0" />,
  info:    <Info       className="w-5 h-5 text-text-muted shrink-0" />,
}

const styles = {
  success: 'border-brand-border bg-brand-tint',
  error:   'border-red-200 bg-red-50',
  info:    'border-ui-border bg-surface-white',
}

// Single Toast item
function ToastItem({ id, type = 'info', message, onDismiss }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(id), 4000)
    return () => clearTimeout(timer)
  }, [id, onDismiss])

  return (
    <div
      role="alert"
      aria-live="polite"
      className={clsx(
        'flex items-start gap-3 w-80 p-4 rounded-lg border shadow-md',
        'animate-slide-in-top',
        styles[type]
      )}
    >
      {icons[type]}
      <p className="text-sm text-text-primary flex-1 leading-snug">{message}</p>
      <button
        onClick={() => onDismiss(id)}
        aria-label="Dismiss notification"
        className="p-0.5 rounded text-text-muted hover:text-text-primary transition-colors shrink-0"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

// Provider 
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const idRef = useRef(0)

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback((message, type = 'info') => {
    const id = ++idRef.current
    setToasts((prev) => {
      // Maximum 3 toasts visible at once
      const next = [...prev, { id, type, message }]
      return next.slice(-3)
    })
  }, [])

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Portal — bottom right */}
      <div
        aria-label="Notifications"
        className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 items-end"
      >
        {toasts.map((t) => (
          <ToastItem key={t.id} {...t} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

//  Hook 
export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}