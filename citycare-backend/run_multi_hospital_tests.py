"""
End-to-end tests for Multi-Hospital System and Role-Based Access Control (RBAC).
"""
import asyncio
from datetime import datetime, timezone, timedelta
import httpx

from app.main import app
from app.core.database import connect_to_mongo, close_mongo_connection, get_db

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  [{tag}] {name}" + (f"  ({detail})" if detail and not condition else ""))
    results.append(bool(condition))


async def main():
    await connect_to_mongo()
    db = get_db()
    # Clean test collections
    await db.appointments.delete_many({})
    await db.hospitals.delete_many({"name": {"$regex": "^Test"}})
    await db.users.delete_many({"email": {"$regex": "@test-rb.com$"}})
    await db.doctors.delete_many({})
    await close_mongo_connection()

    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:

            print("\n== 1. SEED / AUTH SETUP ==")
            # Signup Patient
            r = await c.post("/auth/signup", json={
                "first_name": "Alice", "last_name": "Smith",
                "email": "alice@test-rb.com", "mobile": "+919876543210",
                "password": "password123"
            })
            check("Patient Signup -> 201", r.status_code == 201, r.text)

            r = await c.post("/auth/login", json={"email": "alice@test-rb.com", "password": "password123"})
            check("Patient Login -> 200", r.status_code == 200, r.text)
            patient_tok = r.json()["access_token"]
            hdr_patient = {"Authorization": f"Bearer {patient_tok}"}

            # Create Super Admin directly in DB for testing
            db = get_db()
            from app.core.security import hash_password
            sa_res = await db.users.insert_one({
                "first_name": "Super", "last_name": "Admin",
                "email": "super@test-rb.com", "mobile": "+919000000010",
                "password": hash_password("super123"),
                "role": "super_admin"
            })
            sa_id = str(sa_res.inserted_id)

            r = await c.post("/auth/login", json={"email": "super@test-rb.com", "password": "super123"})
            check("Super Admin Login -> 200", r.status_code == 200, r.text)
            sa_tok = r.json()["access_token"]
            hdr_sa = {"Authorization": f"Bearer {sa_tok}"}

            print("\n== 2. SUPER ADMIN ENDPOINTS ==")
            # Check unauthorized access by patient
            r = await c.get("/super-admin/hospitals", headers=hdr_patient)
            check("Patient denied Super Admin route -> 403", r.status_code == 403, r.text)

            # Create Hospital
            r = await c.post("/super-admin/hospitals", headers=hdr_sa, json={
                "name": "Test Memorial Hospital",
                "address": "123 Test Street",
                "city": "Test City",
                "contact_phone": "+919876500000",
                "email": "info@testmemorial.com"
            })
            check("Create Hospital -> 201", r.status_code == 201, r.text)
            hospital_id = r.json()["id"]

            # List Hospitals
            r = await c.get("/super-admin/hospitals", headers=hdr_sa)
            check("List Hospitals -> 200", r.status_code == 200 and len(r.json()) >= 1)

            # Assign Hospital Admin
            r = await c.post("/super-admin/hospital-admins", headers=hdr_sa, json={
                "first_name": "Harry", "last_name": "Admin",
                "email": "hadmin@test-rb.com", "mobile": "+919876500001",
                "password": "hadminpassword",
                "hospital_id": hospital_id
            })
            check("Create Hospital Admin -> 201", r.status_code == 201, r.text)

            # Login Hospital Admin
            r = await c.post("/auth/login", json={"email": "hadmin@test-rb.com", "password": "hadminpassword"})
            check("Hospital Admin Login -> 200", r.status_code == 200, r.text)
            ha_tok = r.json()["access_token"]
            hdr_ha = {"Authorization": f"Bearer {ha_tok}"}

            # Super Admin Stats
            r = await c.get("/super-admin/analytics", headers=hdr_sa)
            check("Super Admin Analytics -> 200", r.status_code == 200 and "total_hospitals" in r.json())

            print("\n== 3. HOSPITAL ADMIN ENDPOINTS ==")
            # Onboard Doctor
            r = await c.post("/hospital-admin/doctors", headers=hdr_ha, json={
                "first_name": "David", "last_name": "Heart",
                "email": "dr.david@test-rb.com", "mobile": "+919876500002",
                "password": "doctorpassword",
                "hospital_id": hospital_id,
                "specialization": "Cardiology",
                "qualification": "MD Cardiology",
                "consultation_fee": 800.0,
                "bio": "Expert cardiologist",
                "available_days": ["Monday", "Wednesday", "Friday"]
            })
            check("Onboard Doctor -> 201", r.status_code == 201, r.text)
            doctor_id = r.json()["id"]

            # List Hospital Doctors
            r = await c.get("/hospital-admin/doctors", headers=hdr_ha)
            check("List Hospital Doctors -> 200", r.status_code == 200 and len(r.json()) >= 1)

            # Login Doctor
            r = await c.post("/auth/login", json={"email": "dr.david@test-rb.com", "password": "doctorpassword"})
            check("Doctor Login -> 200", r.status_code == 200, r.text)
            doc_tok = r.json()["access_token"]
            hdr_doc = {"Authorization": f"Bearer {doc_tok}"}

            print("\n== 4. PATIENT DISCOVERY & MULTI-HOSPITAL BOOKING ==")
            # Discover Hospitals
            r = await c.get("/clinic/hospitals")
            check("Public List Hospitals -> 200", r.status_code == 200 and len(r.json()) >= 1)

            # Discover Doctors
            r = await c.get(f"/clinic/doctors?hospital_id={hospital_id}")
            check("Public List Doctors for Hospital -> 200", r.status_code == 200 and len(r.json()) >= 1)

            # Book Appointment with hospital_id and doctor_id
            tomorrow = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
            r = await c.post("/appointments", headers=hdr_patient, json={
                "hospital_id": hospital_id,
                "doctor_id": doctor_id,
                "date": tomorrow,
                "slot": "10:00",
                "reason": "Chest tightness and palpitations",
                "symptoms": ["bodyache"]
            })
            check("Book Multi-Hospital Appointment -> 201", r.status_code == 201, r.text)
            appt_id = r.json()["id"]
            check("Response contains hospital and doctor info", r.json()["doctor_id"] == doctor_id)

            print("\n== 5. DOCTOR WORKFLOW & STATUS UPDATES ==")
            # Doctor views assigned appointments
            r = await c.get("/doctor/appointments", headers=hdr_doc)
            check("Doctor List Appointments -> 200", r.status_code == 200 and len(r.json()) >= 1)

            # Doctor updates appointment status to CONFIRMED
            r = await c.patch(f"/doctor/appointments/{appt_id}/status", headers=hdr_doc, json={
                "status": "CONFIRMED",
                "notes": "Patient requested morning slot"
            })
            check("Doctor Confirm Appointment -> 200", r.status_code == 200 and r.json()["status"].upper() == "CONFIRMED")

            # Doctor Dashboard Summary Stats
            r = await c.get("/doctor/dashboard-summary", headers=hdr_doc)
            check("Doctor Summary Stats -> 200", r.status_code == 200 and "pending_count" in r.json())

            # Doctor completes appointment
            r = await c.patch(f"/doctor/appointments/{appt_id}/status", headers=hdr_doc, json={
                "status": "COMPLETED",
                "notes": "Prescribed EKG and medication"
            })
            check("Doctor Complete Appointment -> 200", r.status_code == 200 and r.json()["status"].upper() == "COMPLETED")

    print("\n" + "=" * 40)
    total = len(results)
    passed = sum(results)
    print(f"  {passed}/{total} Multi-Hospital RBAC checks passed")
    print("=" * 40)
    return passed == total

if __name__ == "__main__":
    ok = asyncio.run(main())
    raise SystemExit(0 if ok else 1)
