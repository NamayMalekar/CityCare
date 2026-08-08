"""
Seed multi-hospital system data: Super Admin, Hospital, Hospital Admin, Doctor, and Patient.
"""
import asyncio
import logging
from datetime import datetime, timezone

from app.core.database import connect_to_mongo, close_mongo_connection, get_db
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("citycare.seed")

SUPER_ADMIN_EMAIL = "superadmin@citycare.com"
SUPER_ADMIN_PASSWORD = "admin123"

HOSPITAL_ADMIN_EMAIL = "admin.metro@citycare.com"
HOSPITAL_ADMIN_PASSWORD = "admin123"

DOCTOR_EMAIL = "dr.meera@citycare.clinic"
DOCTOR_PASSWORD = "doctor123"

PATIENT_EMAIL = "asha@test.com"
PATIENT_PASSWORD = "secret123"


async def main() -> None:
    await connect_to_mongo()
    db = get_db()

    # 1. Create Default Hospital
    hospital = await db.hospitals.find_one({"name": "CityCare Central Hospital"})
    if not hospital:
        h_doc = {
            "name": "CityCare Central Hospital",
            "address": "100 Health Avenue, Suite 400",
            "city": "Metro City",
            "contact_phone": "+919876543210",
            "email": "contact@metro.citycare.clinic",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = await db.hospitals.insert_one(h_doc)
        hospital_id = res.inserted_id
        logger.info("Created default hospital: CityCare Central Hospital")
    else:
        hospital_id = hospital["_id"]

    # 2. Super Admin Account
    sa = await db.users.find_one({"email": SUPER_ADMIN_EMAIL})
    if not sa:
        await db.users.insert_one({
            "first_name": "Super",
            "last_name": "Admin",
            "email": SUPER_ADMIN_EMAIL,
            "mobile": "+919000000001",
            "password": hash_password(SUPER_ADMIN_PASSWORD),
            "role": "super_admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Super Admin created: %s", SUPER_ADMIN_EMAIL)
    else:
        await db.users.update_one({"email": SUPER_ADMIN_EMAIL}, {"$set": {"role": "super_admin"}})

    # 3. Hospital Admin Account
    ha = await db.users.find_one({"email": HOSPITAL_ADMIN_EMAIL})
    if not ha:
        await db.users.insert_one({
            "first_name": "Hospital",
            "last_name": "Admin",
            "email": HOSPITAL_ADMIN_EMAIL,
            "mobile": "+919000000002",
            "password": hash_password(HOSPITAL_ADMIN_PASSWORD),
            "role": "hospital_admin",
            "hospital_id": hospital_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Hospital Admin created: %s", HOSPITAL_ADMIN_EMAIL)
    else:
        await db.users.update_one({"email": HOSPITAL_ADMIN_EMAIL}, {"$set": {"role": "hospital_admin", "hospital_id": hospital_id}})

    # 4. Doctor Account
    doc_user = await db.users.find_one({"email": DOCTOR_EMAIL})
    if not doc_user:
        res = await db.users.insert_one({
            "first_name": "Meera",
            "last_name": "Kulkarni",
            "email": DOCTOR_EMAIL,
            "mobile": "+919999999999",
            "password": hash_password(DOCTOR_PASSWORD),
            "role": "doctor",
            "hospital_id": hospital_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        doc_user_id = res.inserted_id
        logger.info("Doctor user created: %s", DOCTOR_EMAIL)
    else:
        doc_user_id = doc_user["_id"]
        await db.users.update_one({"email": DOCTOR_EMAIL}, {"$set": {"role": "doctor", "hospital_id": hospital_id}})

    doc_profile = await db.doctors.find_one({"user_id": doc_user_id})
    if not doc_profile:
        await db.doctors.insert_one({
            "user_id": doc_user_id,
            "hospital_id": hospital_id,
            "specialization": "Cardiology & General Medicine",
            "qualification": "MD, MBBS",
            "consultation_fee": 750.0,
            "bio": "Senior Consultant Physician with 12+ years experience.",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Doctor profile created for Dr. Meera Kulkarni")

    # 5. Patient Account
    patient = await db.users.find_one({"email": PATIENT_EMAIL})
    if not patient:
        await db.users.insert_one({
            "first_name": "Asha",
            "last_name": "Rao",
            "email": PATIENT_EMAIL,
            "mobile": "+919876543210",
            "password": hash_password(PATIENT_PASSWORD),
            "role": "patient",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Patient user created: %s", PATIENT_EMAIL)

    print("\n========================================================")
    print(" Multi-Hospital Accounts Seeded:")
    print(f"   SUPER_ADMIN:    {SUPER_ADMIN_EMAIL} / {SUPER_ADMIN_PASSWORD}")
    print(f"   HOSPITAL_ADMIN: {HOSPITAL_ADMIN_EMAIL} / {HOSPITAL_ADMIN_PASSWORD}")
    print(f"   DOCTOR:         {DOCTOR_EMAIL} / {DOCTOR_PASSWORD}")
    print(f"   PATIENT:        {PATIENT_EMAIL} / {PATIENT_PASSWORD}")
    print("========================================================\n")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
