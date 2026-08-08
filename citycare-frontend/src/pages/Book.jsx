import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { api } from '../api/client';
import { Banner, Spinner } from '../components/ui';
import { DateStrip, SlotGrid } from '../components/domain';
import { bookingWindow, todayISO, prettyDate } from '../utils/dates';

const SYMPTOMS = ['fever', 'cough', 'cold', 'bodyache', 'headache', 'other'];

export default function Book() {
  const location = useLocation();
  const days = bookingWindow(8);

  const [hospitals, setHospitals] = useState([]);
  const [doctors, setDoctors] = useState([]);

  const [selectedHospital, setSelectedHospital] = useState(location.state?.hospitalId || null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);

  const [date, setDate] = useState(todayISO());
  const [slots, setSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);

  const [reason, setReason] = useState('');
  const [temperature, setTemperature] = useState('');
  const [symptoms, setSymptoms] = useState([]);

  const [banner, setBanner] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [confirmed, setConfirmed] = useState(null);

  // Load initial hospitals & doctors
  useEffect(() => {
    async function loadInitial() {
      try {
        const [hList, dList] = await Promise.all([
          api.listHospitals(),
          api.listDoctors(),
        ]);
        setHospitals(hList);
        setDoctors(dList);
        if (!selectedHospital && hList.length > 0) {
          setSelectedHospital(hList[0].id);
        }
      } catch (err) {
        setBanner(err.message);
      }
    }
    loadInitial();
  }, []);

  // When selectedHospital changes, filter available doctors
  const availableDoctors = doctors.filter(
    (d) => !selectedHospital || d.hospital_id === selectedHospital
  );

  // Auto select first doctor if current selected is not in hospital
  useEffect(() => {
    if (availableDoctors.length > 0) {
      if (!selectedDoctor || !availableDoctors.some((d) => d.id === selectedDoctor)) {
        setSelectedDoctor(availableDoctors[0].id);
      }
    } else {
      setSelectedDoctor(null);
    }
  }, [selectedHospital, doctors]);

  // Load free slots when doctor or date changes
  async function loadSlots(forDate, docId, hospId) {
    setSlotsLoading(true);
    setBanner('');
    setSelectedSlot(null);
    try {
      const res = await api.freeSlots(forDate, docId, hospId);
      setSlots(res.free_slots);
    } catch (err) {
      setBanner(err.message);
      setSlots([]);
    } finally {
      setSlotsLoading(false);
    }
  }

  useEffect(() => {
    loadSlots(date, selectedDoctor, selectedHospital);
  }, [date, selectedDoctor, selectedHospital]);

  function toggleSymptom(s) {
    setSymptoms((cur) => (cur.includes(s) ? cur.filter((x) => x !== s) : [...cur, s]));
  }

  const reasonTooShort = reason.trim().length > 0 && reason.trim().length < 10;
  const canSubmit = selectedSlot && reason.trim().length >= 10 && !submitting;

  async function onSubmit(ev) {
    ev.preventDefault();
    setBanner('');
    if (!selectedSlot) {
      setBanner('Please pick a time slot first.');
      return;
    }
    if (reason.trim().length < 10) {
      setBanner('Please give a proper reason — at least 10 characters.');
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        hospital_id: selectedHospital,
        doctor_id: selectedDoctor,
        date,
        slot: selectedSlot,
        reason: reason.trim(),
        symptoms,
      };
      if (temperature !== '') payload.temperature = Number(temperature);

      const appt = await api.book(payload);
      setConfirmed(appt);
    } catch (err) {
      if (err.status === 409) {
        setBanner('That slot just got booked — please pick another.');
        setSelectedSlot(null);
        loadSlots(date, selectedDoctor, selectedHospital);
      } else {
        setBanner(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (confirmed) {
    return (
      <BookingSummary
        appt={confirmed}
        onBookAnother={() => {
          setConfirmed(null);
          setReason('');
          setTemperature('');
          setSymptoms([]);
          setSelectedSlot(null);
          loadSlots(date, selectedDoctor, selectedHospital);
        }}
      />
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-8 fade-up">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
            Book an appointment
          </h1>
          <p className="mt-1 text-sm text-sage">
            Select hospital, doctor, date and time slot for your consultation.
          </p>
        </div>
        <Link to="/dashboard" className="btn-ghost text-sm">
          ← Back
        </Link>
      </div>

      {banner && (
        <div className="mb-4">
          <Banner onClose={() => setBanner('')}>{banner}</Banner>
        </div>
      )}

      <form onSubmit={onSubmit} className="flex flex-col gap-6">
        {/* Step 1: Hospital & Doctor Selector */}
        <section className="card p-5">
          <StepLabel n="1" title="Select Hospital & Doctor" />

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <span className="label">1A. Hospital Facility</span>
              <select
                className="field"
                value={selectedHospital || ''}
                onChange={(e) => setSelectedHospital(e.target.value)}
              >
                {hospitals.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.name} ({h.city})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <span className="label">1B. Doctor Specialist</span>
              <select
                className="field"
                value={selectedDoctor || ''}
                onChange={(e) => setSelectedDoctor(e.target.value)}
                disabled={availableDoctors.length === 0}
              >
                {availableDoctors.length === 0 ? (
                  <option value="">No doctors at this hospital</option>
                ) : (
                  availableDoctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name || `Dr. ${d.first_name} ${d.last_name}`} - {d.specialization} (₹{d.consultation_fee})
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>
        </section>

        {/* Step 2: Date Selector */}
        <section className="card p-5">
          <StepLabel n="2" title="Choose a date" />
          <DateStrip days={days} selected={date} onSelect={setDate} />
        </section>

        {/* Step 3: Time Slot Selector */}
        <section className="card p-5">
          <StepLabel n="3" title={`Available slots for ${prettyDate(date)}`} />
          {slotsLoading ? (
            <Spinner label="Checking doctor availability…" />
          ) : (
            <SlotGrid slots={slots} selected={selectedSlot} onSelect={setSelectedSlot} />
          )}
        </section>

        {/* Step 4: Visit Details */}
        <section className="card p-5">
          <StepLabel n="4" title="Tell the doctor about your visit" />
          <div className="flex flex-col gap-4">
            <label className="block">
              <span className="label">Reason for visit</span>
              <textarea
                className="field min-h-[90px] resize-y"
                placeholder="e.g. Persistent fever and throat pain since yesterday"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
              <span className={'mt-1 block text-xs ' + (reasonTooShort ? 'text-red-600' : 'text-sage')}>
                {reasonTooShort
                  ? `A little more detail, please (${reason.trim().length}/10).`
                  : 'At least 10 characters required.'}
              </span>
            </label>

            <label className="block max-w-[220px]">
              <span className="label">Temperature °F (if fever)</span>
              <input
                type="number"
                step="0.1"
                min="95"
                max="110"
                className="field"
                placeholder="e.g. 101.4"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
              />
              <span className="mt-1 block text-xs text-sage">Optional · 95–110</span>
            </label>

            <div>
              <span className="label">Symptoms</span>
              <div className="flex flex-wrap gap-2">
                {SYMPTOMS.map((s) => {
                  const on = symptoms.includes(s);
                  return (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleSymptom(s)}
                      className={
                        'rounded-full border px-3.5 py-1.5 text-sm font-medium capitalize transition-all ' +
                        (on
                          ? 'border-moss bg-moss/10 text-moss'
                          : 'border-mist bg-card text-sage hover:border-moss')
                      }
                    >
                      {on ? '✓ ' : ''}
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        <div className="pt-1">
          <button
            type="submit"
            className="btn-accent w-full py-3 text-base shadow-lift"
            disabled={!canSubmit}
          >
            {submitting
              ? 'Booking…'
              : selectedSlot
              ? `Confirm ${selectedSlot} on ${prettyDate(date).split(',')[0]}`
              : 'Pick a slot to continue'}
          </button>
        </div>
      </form>
    </div>
  );
}

function StepLabel({ n, title }) {
  return (
    <div className="mb-4 flex items-center gap-2.5">
      <span className="grid h-6 w-6 place-items-center rounded-full bg-pine text-xs font-bold text-cream">
        {n}
      </span>
      <h2 className="font-display text-lg font-medium text-ink">{title}</h2>
    </div>
  );
}

function BookingSummary({ appt, onBookAnother }) {
  return (
    <div className="mx-auto max-w-md px-5 py-16 text-center fade-up">
      <div className="mx-auto mb-5 grid h-16 w-16 place-items-center rounded-full bg-moss/12 text-moss">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path d="M5 13l4 4L19 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <h1 className="font-display text-3xl font-semibold text-ink">You're booked!</h1>
      <p className="mt-2 text-sage">Here's your confirmation details.</p>

      <div className="card mt-6 p-6 text-left space-y-3">
        {appt.hospital_name && <SummaryRow label="Hospital" value={appt.hospital_name} />}
        {appt.doctor_name && <SummaryRow label="Doctor" value={appt.doctor_name} />}
        <SummaryRow label="Date" value={prettyDate(appt.date || appt.appointment_date)} />
        <SummaryRow label="Time Slot" value={appt.slot || appt.time_slot} big />
        <SummaryRow label="Reason" value={appt.reason} />
        {appt.temperature != null && <SummaryRow label="Temperature" value={`${appt.temperature}°F`} />}
        {appt.symptoms?.length > 0 && (
          <SummaryRow label="Symptoms" value={appt.symptoms.join(', ')} />
        )}
      </div>

      <div className="mt-6 flex gap-3">
        <Link to="/dashboard" className="btn-primary flex-1">
          Go to dashboard
        </Link>
        <button onClick={onBookAnother} className="btn-ghost flex-1 border border-mist">
          Book another
        </button>
      </div>
    </div>
  );
}

function SummaryRow({ label, value, big }) {
  return (
    <div className="flex justify-between gap-4 border-b border-mist/70 py-2 last:border-0">
      <span className="text-sm text-sage">{label}</span>
      <span className={'text-right font-medium text-ink ' + (big ? 'font-display text-lg text-pine' : 'text-sm')}>
        {value}
      </span>
    </div>
  );
}
