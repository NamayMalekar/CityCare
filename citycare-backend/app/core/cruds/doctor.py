"""
Doctor CRUD operations.
"""
from typing import Any
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_db
from app.core.security import hash_password
from app.core.models.doctor import doctor_public


async def create_doctor(data: dict[str, Any]) -> dict[str, Any]:
    db = get_db()
    # 1. Create User account with DOCTOR role
    user_doc = {
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"].lower().strip(),
        "mobile": data["mobile"],
        "password": hash_password(data["password"]),
        "role": "DOCTOR",
        "hospital_id": ObjectId(data["hospital_id"]) if data.get("hospital_id") else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    user_res = await db.users.insert_one(user_doc)
    user_id = user_res.inserted_id

    # 2. Create Doctor Profile
    hospital_id = ObjectId(data["hospital_id"]) if data.get("hospital_id") else None
    doctor_doc = {
        "user_id": user_id,
        "hospital_id": hospital_id,
        "specialization": data.get("specialization", "General Medicine"),
        "qualification": data.get("qualification", "MBBS"),
        "consultation_fee": float(data.get("consultation_fee", 500)),
        "bio": data.get("bio", ""),
        "available_days": data.get("available_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    doc_res = await db.doctors.insert_one(doctor_doc)
    doctor_doc["_id"] = doc_res.inserted_id

    # Fetch hospital name if available
    hospital_doc = None
    if hospital_id:
        hospital_doc = await db.hospitals.find_one({"_id": hospital_id})

    return doctor_public(doctor_doc, user_doc, hospital_doc)


async def get_doctor(doctor_id: str) -> dict[str, Any] | None:
    db = get_db()
    try:
        doc = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
        if not doc:
            return None
        user_doc = await db.users.find_one({"_id": doc["user_id"]})
        hospital_doc = await db.hospitals.find_one({"_id": doc["hospital_id"]}) if doc.get("hospital_id") else None
        return doctor_public(doc, user_doc, hospital_doc)
    except Exception:
        return None


async def get_doctor_by_user_id(user_id: str) -> dict[str, Any] | None:
    db = get_db()
    try:
        doc = await db.doctors.find_one({"user_id": ObjectId(user_id)})
        if not doc:
            # Fallback check for legacy doctor
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
            if user_doc and user_doc.get("role", "").upper() == "DOCTOR":
                # Ensure doctor doc exists
                doctor_doc = {
                    "user_id": ObjectId(user_id),
                    "hospital_id": user_doc.get("hospital_id"),
                    "specialization": "General Medicine",
                    "qualification": "MBBS",
                    "consultation_fee": 500.0,
                    "bio": "CityCare Resident Specialist",
                    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                }
                res = await db.doctors.insert_one(doctor_doc)
                doctor_doc["_id"] = res.inserted_id
                doc = doctor_doc
            else:
                return None

        user_doc = await db.users.find_one({"_id": doc["user_id"]})
        hospital_doc = await db.hospitals.find_one({"_id": doc["hospital_id"]}) if doc.get("hospital_id") else None
        return doctor_public(doc, user_doc, hospital_doc)
    except Exception:
        return None


async def list_doctors(hospital_id: str | None = None, specialization: str | None = None) -> list[dict[str, Any]]:
    db = get_db()
    query = {}
    if hospital_id:
        try:
            query["hospital_id"] = ObjectId(hospital_id)
        except Exception:
            query["hospital_id"] = hospital_id
    if specialization:
        query["specialization"] = {"$regex": specialization, "$options": "i"}

    cursor = db.doctors.find(query)
    docs = await cursor.to_list(length=500)
    result = []
    for d in docs:
        user_doc = await db.users.find_one({"_id": d["user_id"]})
        hospital_doc = await db.hospitals.find_one({"_id": d["hospital_id"]}) if d.get("hospital_id") else None
        result.append(doctor_public(d, user_doc, hospital_doc))
    return result


async def update_doctor(doctor_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    db = get_db()
    update_data = {k: v for k, v in data.items() if v is not None}
    if not update_data:
        return await get_doctor(doctor_id)
    try:
        await db.doctors.update_one({"_id": ObjectId(doctor_id)}, {"$set": update_data})
        return await get_doctor(doctor_id)
    except Exception:
        return None


async def delete_doctor(doctor_id: str) -> bool:
    db = get_db()
    try:
        doc = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
        if doc:
            await db.users.delete_one({"_id": doc["user_id"]})
            await db.doctors.delete_one({"_id": ObjectId(doctor_id)})
            return True
        return False
    except Exception:
        return False
