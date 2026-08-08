import { useEffect, useState } from 'react';
import { api, auth } from '../api/client';
import { Spinner, EmptyState, Banner } from '../components/ui';
import { prettyDate } from '../utils/dates';

export default function DoctorDashboard() {
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setBanner(null);
    try {
      const [sData, aList] = await Promise.all([
        api.doctorStats(),
        api.doctorAppointments(statusFilter),
      ]);
      setStats(sData);
      setAppointments(aList);
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleUpdateStatus = async (id, newStatus) => {
    try {
      await api.updateAppointmentStatus(id, newStatus);
      setBanner({ kind: 'success', text: `Appointment updated to ${newStatus}` });
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-1">
        <p className="text-sm font-medium text-sage">Doctor Portal</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          Welcome back, Dr. {auth.name || 'Specialist'}.
        </h1>
      </div>

      {banner && (
        <div className="mb-6">
          <Banner kind={banner.kind} onClose={() => setBanner(null)}>
            {banner.text}
          </Banner>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 mb-8">
        {stats ? (
          <>
            <div className="card p-5 border-l-4 border-terra">
              <span className="text-xs font-semibold uppercase tracking-wider text-sage">
                Pending Requests
              </span>
              <p className="mt-2 font-display text-3xl font-bold text-terra">
                {stats.pending_count ?? 0}
              </p>
              <p className="mt-1 text-xs text-sage">Awaiting confirmation</p>
            </div>
            <div className="card p-5 border-l-4 border-moss bg-moss/5">
              <span className="text-xs font-semibold uppercase tracking-wider text-sage">
                Today's Schedule
              </span>
              <p className="mt-2 font-display text-3xl font-bold text-moss">
                {stats.today_count ?? stats.todays_visits ?? 0}
              </p>
              <p className="mt-1 text-xs text-sage">Scheduled for today</p>
            </div>
            <div className="card p-5 border-l-4 border-pine">
              <span className="text-xs font-semibold uppercase tracking-wider text-sage">
                Upcoming Schedule
              </span>
              <p className="mt-2 font-display text-3xl font-bold text-pine">
                {stats.upcoming_count ?? stats.upcoming_visits ?? 0}
              </p>
              <p className="mt-1 text-xs text-sage">Future bookings</p>
            </div>
          </>
        ) : (
          <div className="sm:col-span-3">
            <Spinner label="Loading doctor stats…" />
          </div>
        )}
      </div>

      {/* Appointment Table section */}
      <section className="card p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-display text-xl font-semibold text-ink">Assigned Appointments</h2>
            <p className="text-xs text-sage">Review patient requests and manage appointment lifecycle.</p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap gap-1.5 rounded-xl border border-mist bg-cream/50 p-1">
            {['ALL', 'PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  statusFilter === st
                    ? 'bg-pine text-white shadow-soft'
                    : 'text-sage hover:text-ink'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <Spinner label="Loading patient appointments…" />
        ) : appointments.length === 0 ? (
          <EmptyState title="No appointments found">
            There are currently no appointments matching the selected status filter.
          </EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-ink">
              <thead>
                <tr className="border-b border-mist bg-cream/40 text-sage uppercase font-semibold">
                  <th className="px-3 py-3">Patient Name</th>
                  <th className="px-3 py-3">Date</th>
                  <th className="px-3 py-3">Time Slot</th>
                  <th className="px-3 py-3">Reason / Symptoms</th>
                  <th className="px-3 py-3">Status</th>
                  <th className="px-3 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-mist">
                {appointments.map((a) => {
                  const statusNorm = (a.status || '').toUpperCase();
                  return (
                    <tr key={a.id} className="hover:bg-cream/20">
                      <td className="px-3 py-3">
                        <div className="font-semibold text-ink">{a.patient_name || 'Patient'}</div>
                        {a.patient_mobile && <div className="text-[11px] text-sage">📞 {a.patient_mobile}</div>}
                      </td>
                      <td className="px-3 py-3 font-medium">{prettyDate(a.date || a.appointment_date)}</td>
                      <td className="px-3 py-3 font-mono text-pine font-semibold">{a.slot || a.time_slot}</td>
                      <td className="px-3 py-3 max-w-xs">
                        <div className="font-medium text-ink/90 truncate">{a.reason}</div>
                        {a.symptoms && a.symptoms.length > 0 && (
                          <div className="mt-0.5 flex flex-wrap gap-1">
                            {a.symptoms.map((s) => (
                              <span key={s} className="rounded bg-mist/60 px-1.5 py-0.2 text-[10px] text-sage">
                                {s}
                              </span>
                            ))}
                          </div>
                        )}
                        {a.temperature && (
                          <div className="mt-0.5 text-[11px] text-terra font-medium">
                            Temp: {a.temperature}°F
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-3">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                            statusNorm === 'CONFIRMED' || statusNorm === 'BOOKED'
                              ? 'bg-moss/10 text-moss'
                              : statusNorm === 'COMPLETED'
                              ? 'bg-pine/10 text-pine'
                              : statusNorm === 'CANCELLED'
                              ? 'bg-red-50 text-red-700'
                              : 'bg-amber-50 text-amber-700'
                          }`}
                        >
                          {statusNorm}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {statusNorm === 'PENDING' && (
                            <button
                              onClick={() => handleUpdateStatus(a.id, 'CONFIRMED')}
                              className="rounded-lg bg-moss px-2.5 py-1 text-xs font-medium text-white hover:bg-moss/90"
                            >
                              Approve
                            </button>
                          )}
                          {(statusNorm === 'PENDING' || statusNorm === 'CONFIRMED' || statusNorm === 'BOOKED') && (
                            <button
                              onClick={() => handleUpdateStatus(a.id, 'COMPLETED')}
                              className="rounded-lg bg-pine px-2.5 py-1 text-xs font-medium text-white hover:bg-pine/90"
                            >
                              Complete
                            </button>
                          )}
                          {statusNorm !== 'CANCELLED' && statusNorm !== 'COMPLETED' && (
                            <button
                              onClick={() => handleUpdateStatus(a.id, 'CANCELLED')}
                              className="rounded-lg border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                            >
                              Cancel
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
