import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { FormInput, Banner, Spinner } from '../components/ui';

export default function HospitalAdminDashboard() {
  const [activeTab, setActiveTab] = useState('roster'); // 'roster' | 'appointments' | 'metrics'
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState(null);

  // Doctor Form State
  const [doctorForm, setDoctorForm] = useState({
    id: null,
    first_name: '',
    last_name: '',
    email: '',
    mobile: '',
    password: '',
    specialization: 'General Medicine',
    qualification: 'MBBS',
    consultation_fee: 500,
    bio: '',
  });
  const [editingDoctor, setEditingDoctor] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dList, aList, mData] = await Promise.all([
        api.hospitalAdminDoctors(),
        api.hospitalAppointments(),
        api.hospitalAdminStats(),
      ]);
      setDoctors(dList);
      setAppointments(aList);
      setMetrics(mData);
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDoctorSubmit = async (e) => {
    e.preventDefault();
    setBanner(null);
    try {
      if (editingDoctor && doctorForm.id) {
        await api.updateDoctor(doctorForm.id, {
          specialization: doctorForm.specialization,
          qualification: doctorForm.qualification,
          consultation_fee: Number(doctorForm.consultation_fee),
          bio: doctorForm.bio,
        });
        setBanner({ kind: 'success', text: 'Doctor profile updated.' });
      } else {
        await api.onboardDoctor(doctorForm);
        setBanner({ kind: 'success', text: `Dr. ${doctorForm.first_name} ${doctorForm.last_name} onboarded successfully!` });
      }
      setDoctorForm({
        id: null,
        first_name: '',
        last_name: '',
        email: '',
        mobile: '',
        password: '',
        specialization: 'General Medicine',
        qualification: 'MBBS',
        consultation_fee: 500,
        bio: '',
      });
      setEditingDoctor(false);
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  const handleEditDoctor = (doc) => {
    setDoctorForm({
      id: doc.id,
      first_name: doc.first_name || '',
      last_name: doc.last_name || '',
      email: doc.email || '',
      mobile: doc.mobile || '',
      password: '',
      specialization: doc.specialization,
      qualification: doc.qualification,
      consultation_fee: doc.consultation_fee,
      bio: doc.bio || '',
    });
    setEditingDoctor(true);
    setActiveTab('roster');
  };

  const handleDeleteDoctor = async (id) => {
    if (!window.confirm('Delete doctor record?')) return;
    try {
      await api.deleteDoctor(id);
      setBanner({ kind: 'success', text: 'Doctor profile deleted.' });
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  if (loading) return <Spinner label="Loading Hospital Administration…" />;

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-block rounded-full bg-moss/10 px-3 py-1 text-xs font-semibold text-moss">
            Hospital Admin Portal
          </span>
          <h1 className="mt-1 font-display text-2xl font-semibold text-ink sm:text-3xl">
            Hospital Operations & Doctor Roster
          </h1>
        </div>
        {metrics && (
          <div className="flex gap-4 rounded-2xl border border-mist bg-white px-4 py-2 text-xs shadow-sm">
            <div>
              <span className="text-sage">Doctors:</span>{' '}
              <strong className="text-ink">{metrics.total_doctors}</strong>
            </div>
            <div>
              <span className="text-sage">Bookings:</span>{' '}
              <strong className="text-ink">{metrics.total_appointments}</strong>
            </div>
            <div>
              <span className="text-sage">Pending:</span>{' '}
              <strong className="text-terra">{metrics.pending_appointments}</strong>
            </div>
          </div>
        )}
      </div>

      {banner && (
        <div className="mb-6">
          <Banner kind={banner.kind} onClose={() => setBanner(null)}>
            {banner.text}
          </Banner>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="mb-8 flex gap-2 border-b border-mist pb-3">
        <button
          onClick={() => setActiveTab('roster')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'roster'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          Doctor Roster ({doctors.length})
        </button>
        <button
          onClick={() => setActiveTab('appointments')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'appointments'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          Hospital Appointments ({appointments.length})
        </button>
        <button
          onClick={() => setActiveTab('metrics')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'metrics'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          Hospital Metrics
        </button>
      </div>

      {/* Tab 1: Doctor Roster */}
      {activeTab === 'roster' && (
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Onboard / Edit Doctor Form */}
          <div className="card h-fit p-6 lg:col-span-1">
            <h2 className="font-display text-lg font-semibold text-ink">
              {editingDoctor ? 'Update Doctor Profile' : 'Onboard New Doctor'}
            </h2>
            <p className="mt-1 text-xs text-sage mb-4">
              {editingDoctor ? 'Edit specialization & consultation fee.' : 'Create doctor account assigned to this hospital.'}
            </p>

            <form onSubmit={handleDoctorSubmit} className="space-y-4">
              {!editingDoctor && (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    <FormInput
                      label="First Name"
                      value={doctorForm.first_name}
                      onChange={(e) => setDoctorForm({ ...doctorForm, first_name: e.target.value })}
                      required
                    />
                    <FormInput
                      label="Last Name"
                      value={doctorForm.last_name}
                      onChange={(e) => setDoctorForm({ ...doctorForm, last_name: e.target.value })}
                      required
                    />
                  </div>
                  <FormInput
                    label="Email Address"
                    type="email"
                    value={doctorForm.email}
                    onChange={(e) => setDoctorForm({ ...doctorForm, email: e.target.value })}
                    placeholder="doctor@hospital.com"
                    required
                  />
                  <FormInput
                    label="Mobile Phone"
                    value={doctorForm.mobile}
                    onChange={(e) => setDoctorForm({ ...doctorForm, mobile: e.target.value })}
                    placeholder="+919876543210"
                    required
                  />
                  <FormInput
                    label="Initial Password"
                    type="password"
                    value={doctorForm.password}
                    onChange={(e) => setDoctorForm({ ...doctorForm, password: e.target.value })}
                    required
                  />
                </>
              )}

              <FormInput
                label="Specialization"
                value={doctorForm.specialization}
                onChange={(e) => setDoctorForm({ ...doctorForm, specialization: e.target.value })}
                placeholder="e.g. Cardiology"
                required
              />

              <FormInput
                label="Qualification"
                value={doctorForm.qualification}
                onChange={(e) => setDoctorForm({ ...doctorForm, qualification: e.target.value })}
                placeholder="e.g. MBBS, MD"
                required
              />

              <FormInput
                label="Consultation Fee (₹)"
                type="number"
                value={doctorForm.consultation_fee}
                onChange={(e) => setDoctorForm({ ...doctorForm, consultation_fee: e.target.value })}
                required
              />

              <label className="block">
                <span className="label">Doctor Bio / Overview</span>
                <textarea
                  className="field py-2"
                  rows="3"
                  value={doctorForm.bio}
                  onChange={(e) => setDoctorForm({ ...doctorForm, bio: e.target.value })}
                  placeholder="Experience, background, specializations..."
                />
              </label>

              <div className="flex gap-2 pt-2">
                <button type="submit" className="btn-primary flex-1">
                  {editingDoctor ? 'Save Changes' : 'Onboard Doctor'}
                </button>
                {editingDoctor && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingDoctor(false);
                      setDoctorForm({
                        id: null,
                        first_name: '',
                        last_name: '',
                        email: '',
                        mobile: '',
                        password: '',
                        specialization: 'General Medicine',
                        qualification: 'MBBS',
                        consultation_fee: 500,
                        bio: '',
                      });
                    }}
                    className="btn-ghost"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Roster Cards */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="font-display text-lg font-semibold text-ink">
              Onboarded Specialists ({doctors.length})
            </h2>

            {doctors.length === 0 ? (
              <div className="card p-8 text-center text-sage">
                No doctors currently onboarded for this hospital. Add your first specialist!
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {doctors.map((doc) => (
                  <div key={doc.id} className="card p-5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="rounded-full bg-moss/10 px-2.5 py-0.5 text-xs font-semibold text-moss">
                          {doc.specialization}
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditDoctor(doc)}
                            className="text-xs text-moss hover:underline font-medium"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteDoctor(doc.id)}
                            className="text-xs text-red-600 hover:underline font-medium"
                          >
                            Remove
                          </button>
                        </div>
                      </div>

                      <h3 className="mt-2 font-display text-base font-semibold text-ink">
                        {doc.name || `Dr. ${doc.first_name} ${doc.last_name}`}
                      </h3>
                      <p className="text-xs text-sage font-medium">{doc.qualification}</p>

                      <p className="mt-2 text-xs text-ink/80 line-clamp-2">
                        {doc.bio || 'No bio provided.'}
                      </p>
                    </div>

                    <div className="mt-4 border-t border-mist/70 pt-3 flex items-center justify-between text-xs">
                      <span className="text-sage">Fee: ₹{doc.consultation_fee}</span>
                      <span className="text-pine font-medium">✉️ {doc.email}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Hospital Appointments */}
      {activeTab === 'appointments' && (
        <div className="card p-6">
          <h2 className="font-display text-lg font-semibold text-ink mb-4">
            Patient Bookings Across Hospital
          </h2>

          {appointments.length === 0 ? (
            <div className="py-8 text-center text-sage">
              No appointments booked at this hospital yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-ink">
                <thead>
                  <tr className="border-b border-mist bg-cream/40 text-sage uppercase font-semibold">
                    <th className="px-3 py-3">Patient</th>
                    <th className="px-3 py-3">Doctor</th>
                    <th className="px-3 py-3">Date</th>
                    <th className="px-3 py-3">Time Slot</th>
                    <th className="px-3 py-3">Reason</th>
                    <th className="px-3 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-mist">
                  {appointments.map((a) => (
                    <tr key={a.id} className="hover:bg-cream/20">
                      <td className="px-3 py-3 font-medium text-ink">{a.patient_name}</td>
                      <td className="px-3 py-3 font-medium text-pine">{a.doctor_name || 'Assigned Specialist'}</td>
                      <td className="px-3 py-3">{a.date || a.appointment_date}</td>
                      <td className="px-3 py-3 font-mono">{a.slot || a.time_slot}</td>
                      <td className="px-3 py-3 max-w-xs truncate">{a.reason}</td>
                      <td className="px-3 py-3">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                            a.status === 'CONFIRMED' || a.status === 'booked'
                              ? 'bg-moss/10 text-moss'
                              : a.status === 'COMPLETED'
                              ? 'bg-pine/10 text-pine'
                              : a.status === 'CANCELLED'
                              ? 'bg-red-50 text-red-700'
                              : 'bg-amber-50 text-amber-700'
                          }`}
                        >
                          {a.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Hospital Metrics */}
      {activeTab === 'metrics' && metrics && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card p-6 flex flex-col">
            <span className="text-xs uppercase font-semibold tracking-wider text-sage">
              Hospital Doctors
            </span>
            <span className="mt-2 font-display text-3xl font-bold text-pine">
              {metrics.total_doctors}
            </span>
          </div>
          <div className="card p-6 flex flex-col">
            <span className="text-xs uppercase font-semibold tracking-wider text-sage">
              Total Appointments
            </span>
            <span className="mt-2 font-display text-3xl font-bold text-ink">
              {metrics.total_appointments}
            </span>
          </div>
          <div className="card p-6 flex flex-col">
            <span className="text-xs uppercase font-semibold tracking-wider text-sage">
              Pending Requests
            </span>
            <span className="mt-2 font-display text-3xl font-bold text-terra">
              {metrics.pending_appointments}
            </span>
          </div>
          <div className="card p-6 flex flex-col">
            <span className="text-xs uppercase font-semibold tracking-wider text-sage">
              Completed Visits
            </span>
            <span className="mt-2 font-display text-3xl font-bold text-moss">
              {metrics.completed_appointments}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
