# CityCare Clinic — Backend

A single-doctor appointment-booking API built with **FastAPI + MongoDB**.
Its one job, done perfectly: **bookings that never double-book**, even under a race.

## Architecture (layered — Day-2 v2 structure)

```
app/
├── main.py            # app wiring, CORS, global error armour, logging
├── core/
│   ├── config.py      # clinic constants + the 12-slot menu (R2, R3)
│   ├── database.py    # Mongo connection + the UNIQUE INDEX (the steel door, R6)
│   ├── security.py    # bcrypt hashing + JWT wristband (R1, R8)
│   └── deps.py        # Gate 1 (401) + doctor-only (403) auth dependencies (R7, R8)
├── schemas/           # Pydantic — Gate 2, validation at the door (R5)
├── models/            # document → response serialization
├── cruds/             # the ONLY layer that touches Mongo
├── controllers/       # business logic — Gates 3 & 4 (R3, R4, R6, R9)
├── routes/            # HTTP endpoints
└── utils/dates.py     # the four ways a date can be wrong (R4)
seed_doctor.py         # creates the one doctor account (R8)
run_tests.py           # 40-check end-to-end suite incl. the race
```

## The four gates (a booking request must pass all, in order)

| Gate | Question | Where | Fail code |
|------|----------|-------|-----------|
| 1 | Who are you? | `core/deps.py` | 401 |
| 2 | Is the data shaped right? | `schemas/appointment.py` | 422 |
| 3 | Does it make business sense? | `controllers/appointment.py` | 400 |
| 4 | Is the slot *still* free (race-safe)? | unique index in Mongo | 409 |

Gate 4 is the **steel door**: a partial unique index on `(date, slot)` where
`status = "booked"`. Two concurrent inserts for the same slot → Mongo lets
exactly one win, the other raises `DuplicateKeyError` → HTTP 409. Because the
index is *partial*, cancelling (flipping status to `cancelled`) frees the slot
again without ever deleting the record.

## Setup

```bash
# 1. MongoDB must be running on localhost:27017

# 2. Create venv + install
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env            # defaults work for local dev

# 4. Seed the one doctor account
python seed_doctor.py
#   email:    dr.meera@citycare.clinic
#   password: doctor123

# 5. Run
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the live, interactive API contract.

## Run the test suite

```bash
python run_tests.py     # 40 checks, in-process, includes the concurrent race
```

## Endpoints

| # | Method | Path | Access | Purpose |
|---|--------|------|--------|---------|
| 1 | POST | `/auth/signup` | open | register a patient |
| 2 | POST | `/auth/login` | open | get the JWT wristband |
| 3 | GET | `/clinic/info` | open | doctor & clinic details |
| 4 | GET | `/clinic/free-slots?date=` | open | free slots for a date |
| 5 | POST | `/appointments` | patient | book a slot |
| 6 | GET | `/appointments/mine` | patient | my own bookings |
| 7 | GET | `/doctor/schedule?date=` | doctor | a day's full schedule |
| 8 | GET | `/doctor/stats` | doctor | clinic stats |
| 9 | PATCH | `/appointments/{id}/cancel` | patient | cancel, frees the slot |

Every timestamp is stored in **UTC**. Every important step is **logged**.
Every failure answers with a clean `{"detail": "..."}`.
