import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, auth } from '../api/client';
import { Spinner, EmptyState, Banner } from '../components/ui';
import { AppointmentCard } from '../components/domain';

export default function Dashboard() {
  const [clinic, setClinic] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancellingId, setCancellingId] = useState(null);

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [info, mine] = await Promise.all([api.clinicInfo(), api.myAppointments()]);
      setClinic(info);
      setAppointments(mine);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onCancel(id) {
    setCancellingId(id);
    setError('');
    try {
      await api.cancel(id);
      // Reflect the change locally — the slot is now free again server-side.
      setAppointments((list) =>
        list.map((a) => (a.id === id ? { ...a, status: 'cancelled' } : a))
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setCancellingId(null);
    }
  }

  const upcoming = appointments.filter((a) => a.status === 'booked');
  const past = appointments.filter((a) => a.status !== 'booked');

  return (
    <div className="mx-auto max-w-5xl px-5 py-8 fade-up">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-sage">Welcome back</p>
          <h1 className="font-display text-3xl font-600 tracking-tight text-ink">
            Hi, {auth.name || 'there'}.
          </h1>
        </div>
        <Link to="/book" className="btn-accent">
          + Book appointment
        </Link>
      </div>

      {error && (
        <div className="mt-5">
          <Banner onClose={() => setError('')}>{error}</Banner>
        </div>
      )}

      {loading ? (
        <Spinner label="Loading your dashboard…" />
      ) : (
        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
          {/* Left: appointments */}
          <section className="order-2 lg:order-1">
            <h2 className="mb-3 font-display text-xl text-ink">Upcoming appointments</h2>
            {upcoming.length === 0 ? (
              <EmptyState
                title="No appointments yet"
                action={
                  <Link to="/book" className="btn-primary mt-2">
                    Book your first slot
                  </Link>
                }
              >
                When you book a slot it'll show up here with its date, time, and status.
              </EmptyState>
            ) : (
              <div className="flex flex-col gap-3">
                {upcoming.map((a) => (
                  <AppointmentCard
                    key={a.id}
                    appt={a}
                    onCancel={onCancel}
                    cancelling={cancellingId === a.id}
                  />
                ))}
              </div>
            )}

            {past.length > 0 && (
              <>
                <h2 className="mb-3 mt-8 font-display text-xl text-ink">Cancelled</h2>
                <div className="flex flex-col gap-3">
                  {past.map((a) => (
                    <AppointmentCard key={a.id} appt={a} />
                  ))}
                </div>
              </>
            )}
          </section>

          {/* Right: doctor & clinic card */}
          <aside className="order-1 lg:order-2">
            {clinic && <ClinicCard clinic={clinic} />}
          </aside>
        </div>
      )}
    </div>
  );
}

function ClinicCard({ clinic }) {
  return (
    <div className="card overflow-hidden">
      <div className="bg-pine px-5 py-6 text-cream">
        <p className="text-xs uppercase tracking-wide text-cream/70">Your doctor</p>
        <h3 className="mt-1 font-display text-2xl">{clinic.doctor_name}</h3>
        <p className="text-sm text-cream/80">{clinic.qualification}</p>
      </div>
      <dl className="divide-y divide-mist">
        <Row term="Clinic" desc={`${clinic.clinic_name}, ${clinic.address}`} />
        <Row term="Morning hours" desc={clinic.morning_hours} />
        <Row term="Evening hours" desc={clinic.evening_hours} />
        <Row term="Per patient" desc={`${clinic.slot_length_minutes} minutes`} />
      </dl>
    </div>
  );
}

function Row({ term, desc }) {
  return (
    <div className="flex items-center justify-between px-5 py-3.5">
      <dt className="text-sm text-sage">{term}</dt>
      <dd className="text-sm font-medium text-ink text-right">{desc}</dd>
    </div>
  );
}
