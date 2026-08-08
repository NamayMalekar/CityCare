import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, auth } from '../api/client';
import { FormInput, Banner } from '../components/ui';
import { AuthShell } from './Login';

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    mobile: '',
    password: '',
    confirm: '',
  });
  const [errors, setErrors] = useState({});
  const [banner, setBanner] = useState('');
  const [loading, setLoading] = useState(false);

  function set(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
    setErrors((e) => ({ ...e, [k]: undefined }));
  }

  function validate() {
    const e = {};
    if (!form.first_name.trim()) e.first_name = 'Required.';
    if (!form.last_name.trim()) e.last_name = 'Required.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Enter a valid email.';
    // +91 pattern: 10 digits starting 6-9, optional +91/91/0 prefix.
    if (!/^(?:\+?91|0)?[6-9]\d{9}$/.test(form.mobile.replace(/\s/g, '')))
      e.mobile = 'Enter a valid Indian mobile number.';
    if (form.password.length < 6) e.password = 'At least 6 characters.';
    if (form.confirm !== form.password) e.confirm = 'Passwords do not match.';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function onSubmit(ev) {
    ev.preventDefault();
    setBanner('');
    if (!validate()) return;
    setLoading(true);
    try {
      // Register, then auto-login so the patient lands straight on the dashboard.
      await api.signup({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        mobile: form.mobile.replace(/\s/g, ''),
        password: form.password,
      });
      const res = await api.login({ email: form.email.trim(), password: form.password });
      auth.set(res.access_token);
      auth.setRole(res.role);
      auth.setName(res.first_name);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setBanner(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="It takes less than a minute.">
      <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        <Banner onClose={() => setBanner('')}>{banner}</Banner>
        <div className="grid grid-cols-2 gap-3">
          <FormInput
            label="First name"
            value={form.first_name}
            onChange={(e) => set('first_name', e.target.value)}
            error={errors.first_name}
          />
          <FormInput
            label="Last name"
            value={form.last_name}
            onChange={(e) => set('last_name', e.target.value)}
            error={errors.last_name}
          />
        </div>
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
          label="Mobile"
          inputMode="tel"
          placeholder="+91 98765 43210"
          value={form.mobile}
          onChange={(e) => set('mobile', e.target.value)}
          error={errors.mobile}
        />
        <div className="grid grid-cols-2 gap-3">
          <FormInput
            label="Password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={(e) => set('password', e.target.value)}
            error={errors.password}
          />
          <FormInput
            label="Confirm"
            type="password"
            autoComplete="new-password"
            value={form.confirm}
            onChange={(e) => set('confirm', e.target.value)}
            error={errors.confirm}
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-sage">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-pine hover:underline">
          Log in
        </Link>
      </p>
    </AuthShell>
  );
}
