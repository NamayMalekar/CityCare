import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, auth } from '../api/client';
import { FormInput, Banner } from '../components/ui';

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [banner, setBanner] = useState('');
  const [loading, setLoading] = useState(false);

  function set(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
    setErrors((e) => ({ ...e, [k]: undefined }));
  }

  function validate() {
    const e = {};
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Enter a valid email.';
    if (!form.password) e.password = 'Enter your password.';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function onSubmit(ev) {
    ev.preventDefault();
    setBanner('');
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.login(form);
      auth.set(res.access_token);
      auth.setRole(res.role);
      auth.setName(res.first_name);
      auth.setHospitalId(res.hospital_id);

      const roleNorm = (res.role || '').toUpperCase();
      let targetPath = '/dashboard';
      if (roleNorm === 'SUPER_ADMIN') targetPath = '/super-admin';
      else if (roleNorm === 'HOSPITAL_ADMIN') targetPath = '/hospital-admin';
      else if (roleNorm === 'DOCTOR') targetPath = '/doctor';

      navigate(targetPath, { replace: true });
    } catch (err) {
      setBanner(err.message);
    } finally {
      setLoading(false);
    }
  }

  const fillQuickDemo = (email, password) => {
    setForm({ email, password });
    setErrors({});
    setBanner('');
  };

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to access your multi-hospital portal."
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        <Banner onClose={() => setBanner('')}>{banner}</Banner>
        <FormInput
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={form.email}
          onChange={(e) => set('email', e.target.value)}
          error={errors.email}
        />
        <FormInput
          label="Password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={form.password}
          onChange={(e) => set('password', e.target.value)}
          error={errors.password}
        />
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Logging in…' : 'Log in'}
        </button>
      </form>

      {/* Quick Demo Logins for Multi-Role Testing */}
      <div className="mt-6 border-t border-mist/80 pt-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-sage mb-2">
          Demo Logins (Click to autofill):
        </p>
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <button
            type="button"
            onClick={() => fillQuickDemo('superadmin@citycare.com', 'admin123')}
            className="rounded-lg border border-mist bg-cream/40 p-2 text-left hover:border-pine hover:bg-cream"
          >
            <span className="font-semibold text-pine block">Super Admin</span>
            <span className="text-sage truncate block">superadmin@citycare.com</span>
          </button>
          <button
            type="button"
            onClick={() => fillQuickDemo('admin.metro@citycare.com', 'admin123')}
            className="rounded-lg border border-mist bg-cream/40 p-2 text-left hover:border-pine hover:bg-cream"
          >
            <span className="font-semibold text-moss block">Hospital Admin</span>
            <span className="text-sage truncate block">admin.metro@citycare.com</span>
          </button>
          <button
            type="button"
            onClick={() => fillQuickDemo('dr.meera@citycare.clinic', 'doctor123')}
            className="rounded-lg border border-mist bg-cream/40 p-2 text-left hover:border-pine hover:bg-cream"
          >
            <span className="font-semibold text-ink block">Doctor</span>
            <span className="text-sage truncate block">dr.meera@citycare.clinic</span>
          </button>
          <button
            type="button"
            onClick={() => fillQuickDemo('asha@test.com', 'secret123')}
            className="rounded-lg border border-mist bg-cream/40 p-2 text-left hover:border-pine hover:bg-cream"
          >
            <span className="font-semibold text-terra block">Patient</span>
            <span className="text-sage truncate block">asha@test.com</span>
          </button>
        </div>
      </div>

      <p className="mt-6 text-center text-sm text-sage">
        New here?{' '}
        <Link to="/signup" className="font-semibold text-pine hover:underline">
          Create an account
        </Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="mx-auto grid min-h-[calc(100vh-64px)] max-w-5xl items-center gap-10 px-5 py-10 lg:grid-cols-2">
      <aside className="hidden lg:block fade-up">
        <p className="mb-3 inline-flex items-center gap-2 rounded-full bg-pine/8 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-pine">
          <span className="h-1.5 w-1.5 rounded-full bg-moss" />
          CityCare Health Platform
        </p>
        <h1 className="font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink">
          Multi-Hospital Care
          <br />
          <span className="text-moss">& Role Control.</span>
        </h1>
        <p className="mt-5 max-w-md text-base leading-relaxed text-sage">
          Streamlined multi-hospital administration, doctor rosters, intelligent scheduling,
          and patient appointment bookings across specialized medical centers.
        </p>
        <dl className="mt-8 grid grid-cols-2 gap-4 max-w-md">
          <div className="card p-4">
            <dt className="text-xs uppercase tracking-wide text-sage">Roles Supported</dt>
            <dd className="font-display text-lg text-ink">Super & Hospital Admins</dd>
          </div>
          <div className="card p-4">
            <dt className="text-xs uppercase tracking-wide text-sage">Specialists</dt>
            <dd className="font-display text-lg text-ink">Multi-Hospital Doctors</dd>
          </div>
        </dl>
      </aside>

      <div className="w-full max-w-md justify-self-center fade-up">
        <div className="card p-7 sm:p-8">
          <h2 className="font-display text-2xl font-semibold text-ink">{title}</h2>
          <p className="mt-1 mb-6 text-sm text-sage">{subtitle}</p>
          {children}
        </div>
      </div>
    </div>
  );
}
