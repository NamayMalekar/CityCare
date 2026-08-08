// A handful of small, shared building blocks.

export function FormInput({ label, error, hint, ...props }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      <input className="field" {...props} />
      {hint && !error && <span className="mt-1 block text-xs text-sage">{hint}</span>}
      {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
    </label>
  );
}

// Error / info banner that shows the backend's `detail` message verbatim.
export function Banner({ kind = 'error', children, onClose }) {
  if (!children) return null;
  const styles = {
    error: 'bg-red-50 text-red-800 border-red-200',
    info: 'bg-pine/5 text-pine border-pine/15',
    success: 'bg-moss/10 text-moss border-moss/25',
  }[kind];
  return (
    <div
      role={kind === 'error' ? 'alert' : 'status'}
      className={`flex items-start justify-between gap-3 rounded-xl border px-4 py-3 text-sm ${styles}`}
    >
      <span>{children}</span>
      {onClose && (
        <button onClick={onClose} className="shrink-0 opacity-60 hover:opacity-100" aria-label="Dismiss">
          ✕
        </button>
      )}
    </div>
  );
}

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-10 text-sage">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-mist border-t-moss" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function EmptyState({ title, children, action }) {
  return (
    <div className="card flex flex-col items-center gap-2 px-6 py-12 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-cream text-sage">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
          <rect x="3" y="5" width="18" height="16" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
          <path d="M8 3v4M16 3v4M3 10h18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      </div>
      <h3 className="font-display text-lg text-ink">{title}</h3>
      {children && <p className="max-w-sm text-sm text-sage">{children}</p>}
      {action}
    </div>
  );
}
