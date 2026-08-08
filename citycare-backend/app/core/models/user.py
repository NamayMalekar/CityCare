"""
User model helpers — the shape of a user document in Mongo and public presentation.
"""
from typing import Any


def user_public(doc: dict[str, Any]) -> dict[str, Any]:
    """Map a raw Mongo user document to a safe representation (no password)."""
    raw_role = doc.get("role", "patient")
    role_str = str(raw_role).lower()

    if role_str in ("super_admin", "superadmin"):
        role = "super_admin"
    elif role_str in ("hospital_admin", "hospitaladmin"):
        role = "hospital_admin"
    elif role_str == "doctor":
        role = "doctor"
    else:
        role = "patient"

    return {
        "id": str(doc["_id"]),
        "first_name": doc.get("first_name", ""),
        "last_name": doc.get("last_name", ""),
        "email": doc.get("email", ""),
        "mobile": doc.get("mobile", ""),
        "role": role,
        "hospital_id": str(doc["hospital_id"]) if doc.get("hospital_id") else None,
    }
