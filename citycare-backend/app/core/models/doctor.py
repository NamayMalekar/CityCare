"""
Doctor model helpers — shape of doctor document in Mongo and public format.
"""
from typing import Any


def doctor_public(doc: dict[str, Any], user_doc: dict[str, Any] | None = None, hospital_doc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Public representation of doctor profile."""
    first_name = doc.get("first_name", "")
    last_name = doc.get("last_name", "")
    email = doc.get("email", "")
    mobile = doc.get("mobile", "")

    if user_doc:
        first_name = user_doc.get("first_name", first_name)
        last_name = user_doc.get("last_name", last_name)
        email = user_doc.get("email", email)
        mobile = user_doc.get("mobile", mobile)

    name = f"Dr. {first_name} {last_name}".strip() if first_name else doc.get("name", "Doctor")

    hospital_name = hospital_doc.get("name", "") if hospital_doc else doc.get("hospital_name", "")

    return {
        "id": str(doc["_id"]),
        "user_id": str(doc.get("user_id", "")),
        "hospital_id": str(doc.get("hospital_id", "")),
        "hospital_name": hospital_name,
        "first_name": first_name,
        "last_name": last_name,
        "name": name,
        "email": email,
        "mobile": mobile,
        "specialization": doc.get("specialization", "General Medicine"),
        "qualification": doc.get("qualification", "MBBS"),
        "consultation_fee": float(doc.get("consultation_fee", 500)),
        "bio": doc.get("bio", ""),
        "available_days": doc.get("available_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
    }
