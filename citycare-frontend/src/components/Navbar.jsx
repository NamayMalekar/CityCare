import { useNavigate, useLocation, Link } from 'react-router-dom';
import { auth } from '../api/client';

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2.5 group">
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-pine text-cream shadow-soft">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path d="M12 5v14M5 12h14" stroke="#D98E4A" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      </span>
      <span className="font-display text-lg font-600 tracking-tight text-ink">
        CityCare<span className="text-moss"> Health</span>
      </span>
    </Link>
  );
}

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = auth.token;
  const role = (auth.role || '').toUpperCase();
  const name = auth.name;

  const onAuthPage = ['/login', '/signup'].includes(location.pathname);

  function logout() {
    auth.clear();
    navigate('/login', { replace: true });
  }

  return (
    <header className="sticky top-0 z-20 border-b border-mist/70 bg-cream/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-3.5">
        <Logo />

        {token ? (
          <div className="flex items-center gap-3">
            {role === 'SUPER_ADMIN' && (
              <NavLink to="/super-admin" current={location.pathname}>
                Super Admin
              </NavLink>
            )}
            {role === 'HOSPITAL_ADMIN' && (
              <NavLink to="/hospital-admin" current={location.pathname}>
                Hospital Admin
              </NavLink>
            )}
            {role === 'DOCTOR' && (
              <NavLink to="/doctor" current={location.pathname}>
                Doctor Portal
              </NavLink>
            )}
            {(role === 'PATIENT' || role === '') && (
              <>
                <NavLink to="/hospitals" current={location.pathname}>
                  Hospitals
                </NavLink>
                <NavLink to="/dashboard" current={location.pathname}>
                  Dashboard
                </NavLink>
                <NavLink to="/book" current={location.pathname}>
                  Book
                </NavLink>
              </>
            )}
            <span className="hidden sm:block text-sm text-sage">
              {name ? `Hi, ${name}` : ''}
            </span>
            <button onClick={logout} className="btn-ghost text-sm">
              Log out
            </button>
          </div>
        ) : (
          !onAuthPage && (
            <Link to="/login" className="btn-primary text-sm">
              Log in
            </Link>
          )
        )}
      </div>
    </header>
  );
}

function NavLink({ to, current, children }) {
  const active = current === to;
  return (
    <Link
      to={to}
      className={
        'hidden sm:inline-block rounded-full px-3 py-1.5 text-sm font-medium transition-colors ' +
        (active ? 'bg-pine/10 text-pine' : 'text-sage hover:text-pine')
      }
    >
      {children}
    </Link>
  );
}
