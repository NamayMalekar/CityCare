const BASE_URL = import.meta.env.VITE_API_URL ?? '';

const TOKEN_KEY = 'citycare_token';

export const auth = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },
  set(token) {
    localStorage.setItem(TOKEN_KEY, token);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('citycare_role');
    localStorage.removeItem('citycare_name');
    localStorage.removeItem('citycare_hospital_id');
  },
  get role() {
    const r = localStorage.getItem('citycare_role');
    return r ? r.toUpperCase() : null;
  },
  setRole(role) {
    localStorage.setItem('citycare_role', role ? role.toUpperCase() : '');
  },
  get name() {
    return localStorage.getItem('citycare_name');
  },
  setName(name) {
    localStorage.setItem('citycare_name', name);
  },
  get hospitalId() {
    return localStorage.getItem('citycare_hospital_id');
  },
  setHospitalId(hospitalId) {
    if (hospitalId) {
      localStorage.setItem('citycare_hospital_id', hospitalId);
    } else {
      localStorage.removeItem('citycare_hospital_id');
    }
  },
};

function extractDetail(data, fallback) {
  if (!data) return fallback;
  const d = data.detail ?? data;
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) {
    return d
      .map((e) => {
        const loc = Array.isArray(e.loc)
          ? e.loc.filter((p) => p !== 'body').join('.')
          : '';
        return loc ? `${loc}: ${e.msg}` : e.msg;
      })
      .join(' | ');
  }
  return fallback;
}

async function request(path, { method = 'GET', body, protected: isProtected = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (isProtected) {
    const t = auth.token;
    if (t) headers['Authorization'] = `Bearer ${t}`;
  }

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new Error(
      'Cannot reach the server. Make sure the backend is running on ' + BASE_URL + '.'
    );
  }

  if (res.status === 401) {
    auth.clear();
    if (window.location.pathname !== '/login') {
      window.location.assign('/login');
    }
    let data = null;
    try {
      data = await res.json();
    } catch {}
    throw new Error(extractDetail(data, 'Please log in again.'));
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const err = new Error(extractDetail(data, 'Something went wrong.'));
    err.status = res.status;
    throw err;
  }
  return data;
}

// ── Public API ───────────────────────────────────────────────────────────────
export const api = {
  // Auth
  signup: (payload) => request('/auth/signup', { method: 'POST', body: payload }),
  login: (payload) => request('/auth/login', { method: 'POST', body: payload }),

  // Clinic & Discovery (Public)
  clinicInfo: () => request('/clinic/info'),
  freeSlots: (date, doctorId, hospitalId) => {
    let url = `/clinic/free-slots?date=${encodeURIComponent(date)}`;
    if (doctorId) url += `&doctor_id=${encodeURIComponent(doctorId)}`;
    if (hospitalId) url += `&hospital_id=${encodeURIComponent(hospitalId)}`;
    return request(url);
  },
  listHospitals: () => request('/clinic/hospitals'),
  listDoctors: (hospitalId, specialization) => {
    let url = '/clinic/doctors';
    const params = [];
    if (hospitalId) params.push(`hospital_id=${encodeURIComponent(hospitalId)}`);
    if (specialization) params.push(`specialization=${encodeURIComponent(specialization)}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    return request(url);
  },

  // Patient (Protected)
  book: (payload) => request('/appointments', { method: 'POST', body: payload, protected: true }),
  myAppointments: () => request('/appointments/mine', { protected: true }),
  cancel: (id) => request(`/appointments/${id}/cancel`, { method: 'PATCH', protected: true }),

  // Doctor (Protected)
  doctorSchedule: (date) =>
    request(`/doctor/schedule?date=${encodeURIComponent(date)}`, { protected: true }),
  doctorStats: () => request('/doctor/stats', { protected: true }),
  doctorAppointments: (statusFilter) => {
    let url = '/doctor/appointments';
    if (statusFilter && statusFilter !== 'ALL') {
      url += `?status=${encodeURIComponent(statusFilter)}`;
    }
    return request(url, { protected: true });
  },
  updateAppointmentStatus: (id, statusVal, notes) =>
    request(`/doctor/appointments/${id}/status`, {
      method: 'PATCH',
      body: { status: statusVal, notes },
      protected: true,
    }),

  // Super Admin (Protected)
  superAdminHospitals: () => request('/super-admin/hospitals', { protected: true }),
  createHospital: (payload) => request('/super-admin/hospitals', { method: 'POST', body: payload, protected: true }),
  updateHospital: (id, payload) => request(`/super-admin/hospitals/${id}`, { method: 'PUT', body: payload, protected: true }),
  deleteHospital: (id) => request(`/super-admin/hospitals/${id}`, { method: 'DELETE', protected: true }),
  createHospitalAdmin: (payload) => request('/super-admin/hospital-admins', { method: 'POST', body: payload, protected: true }),
  superAdminStats: () => request('/super-admin/analytics', { protected: true }),

  // Hospital Admin (Protected)
  hospitalAdminDoctors: () => request('/hospital-admin/doctors', { protected: true }),
  onboardDoctor: (payload) => request('/hospital-admin/doctors', { method: 'POST', body: payload, protected: true }),
  updateDoctor: (id, payload) => request(`/hospital-admin/doctors/${id}`, { method: 'PUT', body: payload, protected: true }),
  deleteDoctor: (id) => request(`/hospital-admin/doctors/${id}`, { method: 'DELETE', protected: true }),
  hospitalAppointments: (statusFilter) => {
    let url = '/hospital-admin/appointments';
    if (statusFilter && statusFilter !== 'ALL') url += `?status=${encodeURIComponent(statusFilter)}`;
    return request(url, { protected: true });
  },
  hospitalAdminStats: () => request('/hospital-admin/analytics', { protected: true }),
};

export { BASE_URL };
