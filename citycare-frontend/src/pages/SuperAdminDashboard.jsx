import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { FormInput, Banner, Spinner } from '../components/ui';

export default function SuperAdminDashboard() {
  const [activeTab, setActiveTab] = useState('hospitals'); // 'hospitals' | 'admins' | 'stats'
  const [stats, setStats] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState(null);

  // Hospital form state
  const [hospitalForm, setHospitalForm] = useState({
    id: null,
    name: '',
    address: '',
    city: '',
    contact_phone: '',
    email: '',
  });
  const [editingHospital, setEditingHospital] = useState(false);

  // Admin form state
  const [adminForm, setAdminForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    mobile: '',
    password: '',
    hospital_id: '',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [hList, sData] = await Promise.all([
        api.superAdminHospitals(),
        api.superAdminStats(),
      ]);
      setHospitals(hList);
      setStats(sData);
      if (hList.length > 0 && !adminForm.hospital_id) {
        setAdminForm((prev) => ({ ...prev, hospital_id: hList[0].id }));
      }
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleHospitalSubmit = async (e) => {
    e.preventDefault();
    setBanner(null);
    try {
      if (editingHospital && hospitalForm.id) {
        await api.updateHospital(hospitalForm.id, hospitalForm);
        setBanner({ kind: 'success', text: 'Hospital updated successfully!' });
      } else {
        await api.createHospital(hospitalForm);
        setBanner({ kind: 'success', text: 'Hospital created successfully!' });
      }
      setHospitalForm({ id: null, name: '', address: '', city: '', contact_phone: '', email: '' });
      setEditingHospital(false);
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  const handleEditHospital = (h) => {
    setHospitalForm({
      id: h.id,
      name: h.name,
      address: h.address,
      city: h.city,
      contact_phone: h.contact_phone || h.phone || '',
      email: h.email,
    });
    setEditingHospital(true);
    setActiveTab('hospitals');
  };

  const handleDeleteHospital = async (id) => {
    if (!window.confirm('Are you sure you want to delete this hospital?')) return;
    try {
      await api.deleteHospital(id);
      setBanner({ kind: 'success', text: 'Hospital removed.' });
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  const handleAdminSubmit = async (e) => {
    e.preventDefault();
    setBanner(null);
    try {
      await api.createHospitalAdmin(adminForm);
      setBanner({ kind: 'success', text: `Hospital Admin account created for ${adminForm.email}` });
      setAdminForm({
        first_name: '',
        last_name: '',
        email: '',
        mobile: '',
        password: '',
        hospital_id: hospitals[0]?.id || '',
      });
      loadData();
    } catch (err) {
      setBanner({ kind: 'error', text: err.message });
    }
  };

  if (loading) return <Spinner label="Loading Super Admin Portal…" />;

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-block rounded-full bg-pine/10 px-3 py-1 text-xs font-semibold text-pine">
            Platform Governance
          </span>
          <h1 className="mt-1 font-display text-2xl font-semibold text-ink sm:text-3xl">
            Super Admin Control Center
          </h1>
        </div>
        {stats && (
          <div className="flex gap-4 rounded-2xl border border-mist bg-white px-4 py-2 text-xs shadow-sm">
            <div>
              <span className="text-sage">Hospitals:</span>{' '}
              <strong className="text-ink">{stats.total_hospitals}</strong>
            </div>
            <div>
              <span className="text-sage">Doctors:</span>{' '}
              <strong className="text-ink">{stats.total_doctors}</strong>
            </div>
            <div>
              <span className="text-sage">Bookings:</span>{' '}
              <strong className="text-ink">{stats.total_appointments}</strong>
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
          onClick={() => setActiveTab('hospitals')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'hospitals'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          Manage Hospitals
        </button>
        <button
          onClick={() => setActiveTab('admins')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'admins'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          Assign Hospital Admin
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'stats'
              ? 'bg-pine text-white shadow-soft'
              : 'text-sage hover:bg-cream hover:text-ink'
          }`}
        >
          System Analytics
        </button>
      </div>

      {/* Tab 1: Hospitals Management */}
      {activeTab === 'hospitals' && (
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Hospital Form */}
          <div className="card h-fit p-6 lg:col-span-1">
            <h2 className="font-display text-lg font-semibold text-ink">
              {editingHospital ? 'Edit Hospital' : 'Register New Hospital'}
            </h2>
            <p className="mt-1 text-xs text-sage mb-4">
              Add healthcare facilities to the CityCare network.
            </p>
            <form onSubmit={handleHospitalSubmit} className="space-y-4">
              <FormInput
                label="Hospital Name"
                value={hospitalForm.name}
                onChange={(e) => setHospitalForm({ ...hospitalForm, name: e.target.value })}
                placeholder="e.g. CityCare Central Hospital"
                required
              />
              <FormInput
                label="City"
                value={hospitalForm.city}
                onChange={(e) => setHospitalForm({ ...hospitalForm, city: e.target.value })}
                placeholder="e.g. Metro City"
                required
              />
              <FormInput
                label="Full Address"
                value={hospitalForm.address}
                onChange={(e) => setHospitalForm({ ...hospitalForm, address: e.target.value })}
                placeholder="e.g. 100 Health Ave"
                required
              />
              <FormInput
                label="Contact Phone"
                value={hospitalForm.contact_phone}
                onChange={(e) => setHospitalForm({ ...hospitalForm, contact_phone: e.target.value })}
                placeholder="+919876543210"
                required
              />
              <FormInput
                label="Official Email"
                type="email"
                value={hospitalForm.email}
                onChange={(e) => setHospitalForm({ ...hospitalForm, email: e.target.value })}
                placeholder="contact@hospital.com"
                required
              />
              <div className="flex gap-2 pt-2">
                <button type="submit" className="btn-primary flex-1">
                  {editingHospital ? 'Update Hospital' : 'Add Hospital'}
                </button>
                {editingHospital && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingHospital(false);
                      setHospitalForm({ id: null, name: '', address: '', city: '', contact_phone: '', email: '' });
                    }}
                    className="btn-ghost"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Hospitals List */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="font-display text-lg font-semibold text-ink">
              Registered Hospitals ({hospitals.length})
            </h2>
            {hospitals.length === 0 ? (
              <div className="card p-8 text-center text-sage">
                No hospitals registered yet. Add your first facility!
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {hospitals.map((h) => (
                  <div key={h.id} className="card p-5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="rounded-full bg-cream px-2.5 py-0.5 text-xs font-medium text-pine">
                          {h.city}
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditHospital(h)}
                            className="text-xs text-moss hover:underline font-medium"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteHospital(h.id)}
                            className="text-xs text-red-600 hover:underline font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      <h3 className="mt-2 font-display text-base font-semibold text-ink">
                        {h.name}
                      </h3>
                      <p className="mt-1 text-xs text-sage">{h.address}</p>
                      <div className="mt-3 text-xs text-ink/80 space-y-1">
                        <p>📞 {h.contact_phone || h.phone}</p>
                        <p>✉️ {h.email}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Assign Hospital Admin */}
      {activeTab === 'admins' && (
        <div className="mx-auto max-w-xl card p-6">
          <h2 className="font-display text-lg font-semibold text-ink">
            Create & Link Hospital Admin Account
          </h2>
          <p className="mt-1 text-xs text-sage mb-6">
            Hospital admins will manage doctors and appointments for their assigned facility.
          </p>

          {hospitals.length === 0 ? (
            <div className="text-center py-6 text-amber-700 bg-amber-50 rounded-xl">
              Please register at least one hospital before assigning administrators.
            </div>
          ) : (
            <form onSubmit={handleAdminSubmit} className="space-y-4">
              <label className="block">
                <span className="label">Assigned Hospital</span>
                <select
                  className="field"
                  value={adminForm.hospital_id}
                  onChange={(e) => setAdminForm({ ...adminForm, hospital_id: e.target.value })}
                  required
                >
                  {hospitals.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.name} ({h.city})
                    </option>
                  ))}
                </select>
              </label>

              <div className="grid grid-cols-2 gap-3">
                <FormInput
                  label="First Name"
                  value={adminForm.first_name}
                  onChange={(e) => setAdminForm({ ...adminForm, first_name: e.target.value })}
                  required
                />
                <FormInput
                  label="Last Name"
                  value={adminForm.last_name}
                  onChange={(e) => setAdminForm({ ...adminForm, last_name: e.target.value })}
                  required
                />
              </div>

              <FormInput
                label="Admin Email"
                type="email"
                value={adminForm.email}
                onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })}
                placeholder="admin@hospital.com"
                required
              />

              <FormInput
                label="Mobile Number"
                value={adminForm.mobile}
                onChange={(e) => setAdminForm({ ...adminForm, mobile: e.target.value })}
                placeholder="+919876543210"
                required
              />

              <FormInput
                label="Temporary Password"
                type="password"
                value={adminForm.password}
                onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })}
                required
              />

              <button type="submit" className="btn-primary w-full mt-2">
                Create Hospital Admin
              </button>
            </form>
          )}
        </div>
      )}

      {/* Tab 3: System Analytics */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="card p-6 flex flex-col">
              <span className="text-xs uppercase font-semibold tracking-wider text-sage">
                Total Hospitals
              </span>
              <span className="mt-2 font-display text-3xl font-bold text-pine">
                {stats.total_hospitals}
              </span>
              <span className="mt-1 text-xs text-sage">Active clinical centers</span>
            </div>
            <div className="card p-6 flex flex-col">
              <span className="text-xs uppercase font-semibold tracking-wider text-sage">
                Total Doctors
              </span>
              <span className="mt-2 font-display text-3xl font-bold text-moss">
                {stats.total_doctors}
              </span>
              <span className="mt-1 text-xs text-sage">Onboarded specialists</span>
            </div>
            <div className="card p-6 flex flex-col">
              <span className="text-xs uppercase font-semibold tracking-wider text-sage">
                Total Bookings
              </span>
              <span className="mt-2 font-display text-3xl font-bold text-terra">
                {stats.total_appointments}
              </span>
              <span className="mt-1 text-xs text-sage">Appointments across platform</span>
            </div>
            <div className="card p-6 flex flex-col">
              <span className="text-xs uppercase font-semibold tracking-wider text-sage">
                Registered Patients
              </span>
              <span className="mt-2 font-display text-3xl font-bold text-ink">
                {stats.total_patients}
              </span>
              <span className="mt-1 text-xs text-sage">Platform patient user accounts</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
