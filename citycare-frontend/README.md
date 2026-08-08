# CityCare Clinic — Frontend

A production-grade **React (Vite) + Tailwind CSS** frontend for the CityCare
Clinic appointment API. It talks only to the backend contract — no mock data.

## Design

A calm, trustworthy clinical identity: deep pine green (`#1C4B3A`), a warm clay
accent (`#D98E4A`) for primary actions, and a soft cream canvas. Display type is
**Fraunces**; body/UI type is **Inter**. One login door routes by role: patients
land on their dashboard, the doctor lands on the clinic view.

## Pages & routes

| Route | Access | What it does |
|-------|--------|--------------|
| `/login` | open | email + password, client-side validation, shows the backend's `detail` on error |
| `/signup` | open | name, email, +91 mobile, password + confirm; auto-logs in on success |
| `/dashboard` | patient | doctor/clinic card + your appointments (cancel frees the slot) |
| `/book` | patient | date strip (today → +7), live free slots, reason/temp/symptoms, conflict-aware submit |
| `/doctor` | doctor only | three stat cards + a date-navigable schedule table |

A patient who visits `/doctor` is redirected to their own dashboard; the API
would 403 them anyway. On any `401` the token is cleared and the user is sent to
`/login`.

## The conflict path

When you submit a booking and the API answers `409` (someone took the slot in
the moment between loading and submitting), the page shows
*"That slot just got booked — please pick another"* and refreshes the slot grid
so you immediately see an accurate menu. This is the visible half of the
backend's steel door.

## Structure

```
src/
├── api/client.js         # ONE fetch wrapper: base URL from .env, Bearer token,
│                         #   {"detail":...} normalization, central 401 handling
├── components/
│   ├── ProtectedRoute.jsx   # auth + role guard
│   ├── Navbar.jsx
│   ├── ui.jsx               # FormInput, Banner, Spinner, EmptyState
│   └── domain.jsx           # DateStrip, SlotGrid, AppointmentCard, StatCard, ScheduleTable
├── pages/                # Login, Signup, Dashboard, Book, DoctorDashboard
├── utils/dates.js        # booking-window + formatting helpers
├── App.jsx               # router + role-based landing
└── main.jsx
```

## Setup

```bash
# Backend must be running first (see ../citycare-backend)

npm install
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm run dev                # http://localhost:5173
```

Log in as the doctor with the seeded account:
`dr.meera@citycare.clinic` / `doctor123`, or sign up as a new patient.

## Build

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build
```

Clean loading / empty / error states on every page, mobile responsive, visible
keyboard focus, and reduced-motion respected.
