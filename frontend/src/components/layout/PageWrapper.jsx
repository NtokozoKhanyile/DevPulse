import clsx from 'clsx'

export function PageWrapper({ children, className }) {
  return (
    <main
      className={clsx(
        'min-h-screen bg-surface-offwhite',
        className
      )}
    >
      {children}
    </main>
  )
}