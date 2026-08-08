# 🏥 CityCare Multi-Hospital Platform & Appointment System

A modern, role-aware Multi-Hospital & Clinic Appointment Platform featuring a **FastAPI backend** and a **React + Tailwind CSS frontend** connected and served on a single unified URL.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/NamayMalekar/CityCare)
[![Single URL](https://img.shields.io/badge/App_URL-http%3A%2F%2Flocalhost%3A8000-brightgreen)](http://localhost:8000)

---

## 🌐 Unified Application URL

Access both the complete React Frontend UI and FastAPI Backend API directly at:
### 👉 **[http://localhost:8000](http://localhost:8000)**

- **Frontend Application**: `http://localhost:8000/`
- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **API Health Check**: `http://localhost:8000/api/health`

---

## ⚡ Quick Start (Single Command)

To build assets, seed accounts, and launch the unified application server:

```powershell
.venv\Scripts\python.exe start_unified.py
```

Open your browser to **[http://localhost:8000](http://localhost:8000)**.

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `superadmin@citycare.com` | `admin123` | Platform-wide analytics, hospital management, system oversight |
| **Hospital Admin** | `admin.nagpur@citycare.com` | `admin123` | Doctor onboardings, department & slot schedules for Nagpur branch |
| **Doctor** | `dr.meera@citycare.clinic` | `doctor123` | Daily schedule, patient queue, consultation statistics |
| **Patient** | *Sign up directly on UI* | *Chosen at signup* | Multi-hospital search, doctor selection, slot booking, history |

---

## 🏗 System Architecture

```text
CityCare-Clinic/
├── citycare-frontend/          # React + Vite + Tailwind CSS Frontend UI
│   ├── src/
│   │   ├── pages/              # Patient, Doctor, Hospital Admin, Super Admin dashboards
│   │   ├── components/         # Navbar, ProtectedRoute, Domain & UI widgets
│   │   └── api/client.js       # Unified fetch wrapper (Relative / API endpoints)
│   └── dist/                   # Built production static assets
├── citycare-backend/           # FastAPI + Motor (MongoDB) Layered Architecture
│   ├── app/
│   │   ├── routes/             # Auth, Clinic, Appointments, Doctor, Hospital Admin, Super Admin
│   │   ├── controllers/        # Business logic & RBAC permissions
│   │   ├── core/               # Database models, schemas, CRUDs, security (JWT & bcrypt)
│   │   └── main.py             # Dual route mounting (/ & /api) + Static file SPA fallback
│   ├── seed_multi_hospital.py  # Seed script for hospitals, admins, and doctors
│   └── run_multi_hospital_tests.py # Concurrency & RBAC automated test suite
├── start_unified.py            # One-click launcher (Seeds DB + Builds Frontend + Runs Uvicorn)
└── .gitignore                  # Exclusion rules for .venv, node_modules, dist, secrets
```

---

## 🛡 Features & Capabilities

- **Zero Double-Booking Guarantee**: MongoDB unique partial indexes `(date, slot, doctor_id)` ensure race-safe concurrent booking.
- **Multi-Hospital & Multi-Doctor**: Filter by hospital location, department, specialty, and doctor availability.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Super Admin, Hospital Admin, Doctor, and Patient with 401/403 security enforcement.
- **Single-Origin Deployment**: FastAPI serves the React SPA static files and handles API calls under port `8000`.

---

## 🧪 Running Automated Tests

To run the multi-hospital concurrency and RBAC integration test suite:

```powershell
.venv\Scripts\python.exe citycare-backend/run_multi_hospital_tests.py
```

---

## 🔗 Repository Links

- **GitHub Repository**: [https://github.com/NamayMalekar/CityCare](https://github.com/NamayMalekar/CityCare)
- **Local Application URL**: [http://localhost:8000](http://localhost:8000)
