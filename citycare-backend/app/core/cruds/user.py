"""
User CRUD — pure database operations for users collection.
"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import get_db


async def create_user(
    first_name: str,
    last_name: str,
    email: str,
    mobile: str,
    hashed_password: str,
    role: str = "patient",
    hospital_id: str | None = None,
) -> dict | None:
    db = get_db()
    norm_role = role.lower() if isinstance(role, str) else "patient"
    if norm_role in ("super_admin", "superadmin"):
        norm_role = "super_admin"
    elif norm_role in ("hospital_admin", "hospitaladmin"):
        norm_role = "hospital_admin"

    doc = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email.lower().strip(),
        "mobile": mobile,
        "password": hashed_password,
        "role": norm_role,
        "hospital_id": ObjectId(hospital_id) if hospital_id else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError:
        return None
    doc["_id"] = result.inserted_id
    return doc


async def get_user_by_email(email: str) -> dict | None:
    db = get_db()
    return await db.users.find_one({"email": email.lower().strip()})


async def get_user_by_id(user_id: str) -> dict | None:
    db = get_db()
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    return await db.users.find_one({"_id": oid})


async def count_patients() -> int:
    db = get_db()
    return await db.users.count_documents({"role": {"$in": ["patient", "PATIENT"]}})
