import { Navigate } from 'react-router-dom';
import { auth } from '../api/client';

export default function ProtectedRoute({ children, allowedRoles, role }) {
  const token = auth.token;
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const currentRole = (auth.role || 'PATIENT').toUpperCase();
  const roles = allowedRoles
    ? allowedRoles.map((r) => r.toUpperCase())
    : role
    ? [role.toUpperCase()]
    : [];

  if (roles.length > 0 && !roles.includes(currentRole)) {
    // Redirect unauthorized user to their respective dashboard
    let home = '/dashboard';
    if (currentRole === 'SUPER_ADMIN') home = '/super-admin';
    else if (currentRole === 'HOSPITAL_ADMIN') home = '/hospital-admin';
    else if (currentRole === 'DOCTOR') home = '/doctor';

    return <Navigate to={home} replace />;
  }

  return children;
}
