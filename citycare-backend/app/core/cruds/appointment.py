"""
Appointment CRUD — operations on the appointments collection.
"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import get_db


class SlotTakenError(Exception):
    """Raised when slot is already booked."""


async def booked_slots_for_date(date_str: str, doctor_id: str | None = None, hospital_id: str | None = None) -> list[str]:
    """Return the slots already actively booked/confirmed on a given date."""
    db = get_db()
    query: dict[str, Any] = {
        "$or": [
            {"date": date_str},
            {"appointment_date": date_str}
        ],
        "status": {"$in": ["booked", "PENDING", "CONFIRMED"]}
    }
    if doctor_id:
        query["$or"] = [
            {"doctor_id": str(doctor_id)},
            {"doctor_id": None},
            {"doctor_id": {"$exists": False}}
        ]
        # preserve date constraint
        query["date"] = date_str

    cursor = db.appointments.find(query, {"slot": 1, "time_slot": 1, "_id": 0})
    slots = []
    async for doc in cursor:
        slot_val = doc.get("time_slot") or doc.get("slot")
        if slot_val:
            slots.append(slot_val)
    return slots


async def insert_booking(
    *,
    patient_id: str,
    patient_name: str,
    date_str: str,
    slot: str,
    reason: str,
    temperature: float | None = None,
    symptoms: list[str] | None = None,
    hospital_id: str | None = None,
    doctor_id: str | None = None,
    notes: str | None = "",
    status: str = "booked",
) -> dict:
    db = get_db()

    doctor_name = "Doctor"
    hospital_name = "CityCare Hospital"

    if doctor_id:
        try:
            doc_record = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
            if doc_record:
                u_record = await db.users.find_one({"_id": doc_record["user_id"]})
                if u_record:
                    doctor_name = f"Dr. {u_record.get('first_name', '')} {u_record.get('last_name', '')}".strip()
        except Exception:
            pass

    if hospital_id:
        try:
            h_record = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
            if h_record:
                hospital_name = h_record.get("name", hospital_name)
        except Exception:
            pass

    doc = {
        "patient_id": str(patient_id),
        "patient_name": patient_name,
        "hospital_id": str(hospital_id) if hospital_id else None,
        "doctor_id": str(doctor_id) if doctor_id else None,
        "doctor_name": doctor_name,
        "hospital_name": hospital_name,
        "date": date_str,
        "appointment_date": date_str,
        "slot": slot,
        "time_slot": slot,
        "reason": reason,
        "temperature": temperature,
        "symptoms": symptoms or [],
        "notes": notes or "",
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    query: dict[str, Any] = {
        "date": date_str,
        "slot": slot,
        "status": {"$in": ["booked", "PENDING", "CONFIRMED"]}
    }
    if doctor_id:
        query["doctor_id"] = str(doctor_id)

    existing = await db.appointments.find_one(query)
    if existing:
        raise SlotTakenError("This slot is already booked.")

    try:
        result = await db.appointments.insert_one(doc)
    except DuplicateKeyError:
        raise SlotTakenError("This slot is already booked.")

    doc["_id"] = result.inserted_id
    return doc


async def list_for_patient(patient_id: str) -> list[dict]:
    db = get_db()
    cursor = db.appointments.find({"patient_id": str(patient_id)}).sort("created_at", -1)
    return [doc async for doc in cursor]


async def list_for_doctor(doctor_id: str, status: str | None = None) -> list[dict]:
    db = get_db()
    query: dict[str, Any] = {
        "$or": [
            {"doctor_id": str(doctor_id)},
            {"doctor_id": None},
            {"doctor_id": {"$exists": False}}
        ]
    }
    if status:
        query["status"] = {"$in": [status.lower(), status.upper()]}
    cursor = db.appointments.find(query).sort("created_at", -1)
    return [doc async for doc in cursor]


async def list_for_hospital(hospital_id: str, status: str | None = None) -> list[dict]:
    db = get_db()
    query: dict[str, Any] = {"hospital_id": str(hospital_id)}
    if status:
        query["status"] = {"$in": [status.lower(), status.upper()]}
    cursor = db.appointments.find(query).sort("created_at", -1)
    return [doc async for doc in cursor]


async def list_all_appointments(status: str | None = None) -> list[dict]:
    db = get_db()
    query: dict[str, Any] = {}
    if status:
        query["status"] = {"$in": [status.lower(), status.upper()]}
    cursor = db.appointments.find(query).sort("created_at", -1)
    return [doc async for doc in cursor]


async def list_for_date(date_str: str, doctor_id: str | None = None) -> list[dict]:
    db = get_db()
    query: dict[str, Any] = {
        "$or": [{"date": date_str}, {"appointment_date": date_str}]
    }
    if doctor_id:
        query["$or"] = [
            {"doctor_id": str(doctor_id)},
            {"doctor_id": None},
            {"doctor_id": {"$exists": False}}
        ]
        query["date"] = date_str
    cursor = db.appointments.find(query).sort("slot", 1)
    return [doc async for doc in cursor]


async def get_by_id(appointment_id: str) -> dict | None:
    db = get_db()
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        return None
    return await db.appointments.find_one({"_id": oid})


async def update_status(appointment_id: str, new_status: str, notes: str | None = None) -> dict | None:
    db = get_db()
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        return None

    update_fields: dict[str, Any] = {"status": new_status.lower()}
    if notes is not None:
        update_fields["notes"] = notes
    if new_status.lower() in ("cancelled", "cancelled"):
        update_fields["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    await db.appointments.update_one({"_id": oid}, {"$set": update_fields})
    return await get_by_id(appointment_id)


async def cancel(appointment_id: str) -> bool:
    db = get_db()
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        return False
    app_doc = await db.appointments.find_one({"_id": oid})
    if not app_doc or app_doc.get("status") in ("cancelled", "CANCELLED"):
        return False

    result = await db.appointments.update_one(
        {"_id": oid},
        {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc).isoformat()}},
    )
    return result.modified_count == 1


async def count_on_date(date_str: str, doctor_id: str | None = None) -> int:
    db = get_db()
    query: dict[str, Any] = {
        "$or": [{"date": date_str}, {"appointment_date": date_str}],
        "status": {"$in": ["booked", "PENDING", "CONFIRMED", "pending", "confirmed"]}
    }
    if doctor_id:
        query["doctor_id"] = str(doctor_id)
    return await db.appointments.count_documents(query)


async def count_upcoming(from_date_str: str, doctor_id: str | None = None) -> int:
    db = get_db()
    query: dict[str, Any] = {
        "$or": [{"date": {"$gt": from_date_str}}, {"appointment_date": {"$gt": from_date_str}}],
        "status": {"$in": ["booked", "PENDING", "CONFIRMED", "pending", "confirmed"]}
    }
    if doctor_id:
        query["doctor_id"] = str(doctor_id)
    return await db.appointments.count_documents(query)
