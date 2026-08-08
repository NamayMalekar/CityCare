# CityCare Clinic — Appointment Booking System

A complete, working appointment-booking product for a single-doctor clinic, with
two roles (**patient** and **doctor**). Built to the Day-4 brief: a backend that
**refuses to double-book**, and a clean role-aware frontend.

```
citycare-backend/    FastAPI + MongoDB  — the API (handwritten, layered)
citycare-frontend/   React + Vite + Tailwind — the UI
```

Each folder has its own README with full setup steps. The short version:

## 1. Backend

```bash
cd citycare-backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# MongoDB must be running on localhost:27017
python seed_doctor.py                 # creates dr.meera@citycare.clinic / doctor123
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs · Run the test suite: `python run_tests.py`

## 2. Frontend

```bash
cd citycare-frontend
npm install
cp .env.example .env                  # VITE_API_URL=http://localhost:8000
npm run dev                           # http://localhost:5173
```

## What it does

- **Patients** sign up, log in, see the doctor's info and the *genuinely free*
  slots for a date (today → 7 days), book with a reason / temperature / symptoms,
  see only their own appointments, and cancel (which frees the slot again).
- **The doctor** logs in through the same door and lands on a private dashboard:
  registered-patient count, today's and upcoming visit counts, and the full
  schedule for any day (time, patient name, reason, temperature, symptoms).

## The one thing that matters: no double-booking

Two patients can never hold the same slot. The guarantee is enforced by a
**unique partial index** on `(date, slot)` in MongoDB — the database's final
word, race-safe even if two requests arrive in the same millisecond. The
included test suite fires four concurrent bookings at one slot and proves exactly
one wins (201) while the rest get a conflict (409).

Four gates guard every booking, each with an honest answer:

1. **401** — Who are you? (no/invalid token)
2. **422** — Is the data shaped right? (reason too short, impossible temperature, unknown symptom)
3. **400** — Does it make business sense? (bad date, past date, beyond the window, slot not on the menu)
4. **409** — Is the slot *still* free? (the steel door)

Authentication (401) and authorization (403) are kept distinct: a valid patient
token knocking on a doctor-only endpoint gets **403 "you may not"**, never 401.

## Demo credentials

- **Doctor:** `dr.meera@citycare.clinic` / `doctor123`
- **Patient:** sign up a fresh account in the app.
