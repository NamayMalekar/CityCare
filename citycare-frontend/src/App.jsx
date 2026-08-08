import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { auth } from './api/client';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Book from './pages/Book';
import Hospitals from './pages/Hospitals';
import DoctorDashboard from './pages/DoctorDashboard';
import SuperAdminDashboard from './pages/SuperAdminDashboard';
import HospitalAdminDashboard from './pages/HospitalAdminDashboard';

function Landing() {
  if (!auth.token) return <Navigate to="/login" replace />;
  const role = (auth.role || 'PATIENT').toUpperCase();
  if (role === 'SUPER_ADMIN') return <Navigate to="/super-admin" replace />;
  if (role === 'HOSPITAL_ADMIN') return <Navigate to="/hospital-admin" replace />;
  if (role === 'DOCTOR') return <Navigate to="/doctor" replace />;
  return <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route
            path="/super-admin"
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <SuperAdminDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/hospital-admin"
            element={
              <ProtectedRoute allowedRoles={['HOSPITAL_ADMIN', 'SUPER_ADMIN']}>
                <HospitalAdminDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/doctor"
            element={
              <ProtectedRoute allowedRoles={['DOCTOR', 'SUPER_ADMIN']}>
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/hospitals"
            element={
              <ProtectedRoute allowedRoles={['PATIENT', 'SUPER_ADMIN']}>
                <Hospitals />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute allowedRoles={['PATIENT', 'SUPER_ADMIN']}>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/book"
            element={
              <ProtectedRoute allowedRoles={['PATIENT', 'SUPER_ADMIN']}>
                <Book />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

function NotFound() {
  return (
    <div className="mx-auto max-w-md px-5 py-24 text-center">
      <p className="font-display text-6xl text-pine">404</p>
      <p className="mt-2 text-sage">That page doesn't exist.</p>
      <a href="/" className="btn-primary mt-6 inline-flex">
        Back home
      </a>
    </div>
  );
}
