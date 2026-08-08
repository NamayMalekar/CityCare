"""
Hospital model helpers — shape of hospital document in Mongo and public format.
"""
from typing import Any
from datetime import datetime, timezone


def hospital_public(doc: dict[str, Any]) -> dict[str, Any]:
    """Public serialization of hospital document."""
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "address": doc.get("address", ""),
        "city": doc.get("city", ""),
        "contact_phone": doc.get("contact_phone", doc.get("phone", "")),
        "email": doc.get("email", ""),
        "created_at": doc.get("created_at") or datetime.now(timezone.utc).isoformat(),
    }
