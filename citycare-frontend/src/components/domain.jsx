// Domain components: slot grid, appointment cards, doctor stat cards, and schedule table.

export function DateStrip({ days, selected, onSelect }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {days.map((d) => {
        const active = d.iso === selected;
        return (
          <button
            key={d.iso}
            type="button"
            onClick={() => onSelect(d.iso)}
            className={
              'flex min-w-[64px] flex-col items-center rounded-xl border px-3 py-2.5 transition-all ' +
              (active
                ? 'border-pine bg-pine text-cream shadow-soft'
                : 'border-mist bg-card text-ink hover:border-moss')
            }
          >
            <span className={'text-[11px] font-semibold uppercase ' + (active ? 'text-cream/80' : 'text-sage')}>
              {d.isToday ? 'Today' : d.weekday}
            </span>
            <span className="font-display text-xl leading-tight">{d.day}</span>
            <span className={'text-[11px] ' + (active ? 'text-cream/80' : 'text-sage')}>{d.month}</span>
          </button>
        );
      })}
    </div>
  );
}

export function SlotGrid({ slots, selected, onSelect }) {
  if (!slots || slots.length === 0) {
    return (
      <p className="rounded-xl bg-cream px-4 py-6 text-center text-sm text-sage">
        No free slots left for this day/doctor. Try another date or doctor.
      </p>
    );
  }
  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
      {slots.map((s) => {
        const active = s === selected;
        return (
          <button
            key={s}
            type="button"
            onClick={() => onSelect(s)}
            className={
              'rounded-xl border px-2 py-3 text-sm font-semibold transition-all ' +
              (active
                ? 'border-clay bg-clay text-ink shadow-soft'
                : 'border-mist bg-card text-ink hover:border-moss hover:bg-moss/5')
            }
          >
            {s}
          </button>
        );
      })}
    </div>
  );
}

export function AppointmentCard({ appt, onCancel, cancelling }) {
  const normStatus = (appt.status || '').toUpperCase();
  const canCancel = normStatus === 'PENDING' || normStatus === 'CONFIRMED' || normStatus === 'BOOKED';

  return (
    <div className="card flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-pine/8 text-pine font-semibold">
          <span className="font-display text-base leading-none">{appt.slot || appt.time_slot}</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <p className="font-display text-base font-semibold text-ink">
              {formatDate(appt.date || appt.appointment_date)}
            </p>
            {appt.hospital_name && (
              <span className="text-xs text-sage font-medium">· {appt.hospital_name}</span>
            )}
          </div>
          {appt.doctor_name && (
            <p className="text-xs font-semibold text-pine mt-0.5">{appt.doctor_name}</p>
          )}
          <p className="mt-1 text-xs text-sage line-clamp-2">{appt.reason}</p>
          {appt.symptoms?.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {appt.symptoms.map((s) => (
                <span key={s} className="rounded-full bg-cream px-2 py-0.5 text-[10px] text-sage">
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="flex items-center gap-3 sm:flex-col sm:items-end">
        <StatusBadge status={normStatus} />
        {canCancel && onCancel && (
          <button
            onClick={() => onCancel(appt.id)}
            disabled={cancelling}
            className="text-xs font-semibold text-red-600 hover:underline disabled:opacity-50"
          >
            {cancelling ? 'Cancelling…' : 'Cancel'}
          </button>
        )}
      </div>
    </div>
  );
}

export function StatusBadge({ status }) {
  const norm = (status || '').toUpperCase();
  const styles = {
    CONFIRMED: 'bg-moss/12 text-moss border-moss/20',
    BOOKED: 'bg-moss/12 text-moss border-moss/20',
    PENDING: 'bg-amber-50 text-amber-700 border-amber-200',
    COMPLETED: 'bg-pine/12 text-pine border-pine/20',
    CANCELLED: 'bg-red-50 text-red-700 border-red-200',
  }[norm] || 'bg-mist text-sage';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${styles}`}>
      {norm}
    </span>
  );
}

export function StatCard({ label, value, accent }) {
  return (
    <div className="card p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-sage">{label}</p>
      <p className={'mt-2 font-display text-4xl leading-none ' + (accent ? 'text-clay' : 'text-ink')}>
        {value}
      </p>
    </div>
  );
}

export function ScheduleTable({ rows }) {
  return (
    <div className="card overflow-hidden">
      <div className="hidden grid-cols-[80px_1.2fr_2fr_90px_1.4fr] gap-4 border-b border-mist bg-cream px-5 py-3 text-xs font-semibold uppercase tracking-wide text-sage sm:grid">
        <span>Time</span>
        <span>Patient</span>
        <span>Reason</span>
        <span>Temp</span>
        <span>Symptoms</span>
      </div>
      <ul className="divide-y divide-mist">
        {rows.map((r) => (
          <li
            key={r.id}
            className="grid grid-cols-1 gap-1 px-5 py-4 sm:grid-cols-[80px_1.2fr_2fr_90px_1.4fr] sm:items-center sm:gap-4"
          >
            <span className="font-display text-lg text-pine sm:text-base">{r.slot || r.time_slot}</span>
            <span className="font-medium text-ink">
              {r.patient_name}
              {(r.status || '').toUpperCase() === 'CANCELLED' && (
                <span className="ml-2 rounded-full bg-mist px-2 py-0.5 text-[10px] font-semibold text-sage">
                  cancelled
                </span>
              )}
            </span>
            <span className="text-sm text-sage">{r.reason}</span>
            <span className="text-sm text-ink">{r.temperature ? `${r.temperature}°F` : '—'}</span>
            <span className="flex flex-wrap gap-1">
              {r.symptoms?.length
                ? r.symptoms.map((s) => (
                    <span key={s} className="rounded-full bg-cream px-2 py-0.5 text-[11px] text-sage">
                      {s}
                    </span>
                  ))
                : '—'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatDate(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}
