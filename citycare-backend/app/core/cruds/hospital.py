"""
Hospital CRUD operations.
"""
from typing import Any
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_db
from app.core.models.hospital import hospital_public


async def create_hospital(data: dict[str, Any]) -> dict[str, Any]:
    db = get_db()
    doc = {
        "name": data["name"],
        "address": data["address"],
        "city": data["city"],
        "contact_phone": data["contact_phone"],
        "email": data["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    res = await db.hospitals.insert_one(doc)
    doc["_id"] = res.inserted_id
    return hospital_public(doc)


async def get_hospital(hospital_id: str) -> dict[str, Any] | None:
    db = get_db()
    try:
        doc = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
        return hospital_public(doc) if doc else None
    except Exception:
        return None


async def list_hospitals() -> list[dict[str, Any]]:
    db = get_db()
    cursor = db.hospitals.find({}).sort("name", 1)
    docs = await cursor.to_list(length=500)
    return [hospital_public(d) for d in docs]


async def update_hospital(hospital_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    db = get_db()
    update_data = {k: v for k, v in data.items() if v is not None}
    if not update_data:
        return await get_hospital(hospital_id)
    try:
        await db.hospitals.update_one({"_id": ObjectId(hospital_id)}, {"$set": update_data})
        return await get_hospital(hospital_id)
    except Exception:
        return None


async def delete_hospital(hospital_id: str) -> bool:
    db = get_db()
    try:
        res = await db.hospitals.delete_one({"_id": ObjectId(hospital_id)})
        return res.deleted_count > 0
    except Exception:
        return False
