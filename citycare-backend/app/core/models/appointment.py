"""
Appointment model helpers — how an appointment document is shaped and
serialized for patient-facing, doctor-facing, and admin views.
"""
from typing import Any


def appointment_public(doc: dict[str, Any]) -> dict[str, Any]:
    """Patient-facing view of one appointment."""
    app_date = doc.get("appointment_date") or doc.get("date", "")
    time_slot = doc.get("time_slot") or doc.get("slot", "")
    status = (doc.get("status") or "PENDING").upper()

    return {
        "id": str(doc["_id"]),
        "hospital_id": str(doc.get("hospital_id")) if doc.get("hospital_id") else None,
        "doctor_id": str(doc.get("doctor_id")) if doc.get("doctor_id") else None,
        "patient_id": str(doc.get("patient_id")) if doc.get("patient_id") else None,
        "date": app_date,
        "appointment_date": app_date,
        "slot": time_slot,
        "time_slot": time_slot,
        "reason": doc.get("reason", ""),
        "temperature": doc.get("temperature"),
        "symptoms": doc.get("symptoms", []),
        "notes": doc.get("notes", ""),
        "status": status,
        "doctor_name": doc.get("doctor_name", ""),
        "hospital_name": doc.get("hospital_name", ""),
        "created_at": doc.get("created_at", ""),
    }


def appointment_for_doctor(doc: dict[str, Any]) -> dict[str, Any]:
    """Doctor-facing view — includes the patient's name and details."""
    app_date = doc.get("appointment_date") or doc.get("date", "")
    time_slot = doc.get("time_slot") or doc.get("slot", "")
    status = (doc.get("status") or "PENDING").upper()

    return {
        "id": str(doc["_id"]),
        "hospital_id": str(doc.get("hospital_id")) if doc.get("hospital_id") else None,
        "doctor_id": str(doc.get("doctor_id")) if doc.get("doctor_id") else None,
        "patient_id": str(doc.get("patient_id")) if doc.get("patient_id") else None,
        "patient_name": doc.get("patient_name", "Patient"),
        "patient_email": doc.get("patient_email", ""),
        "patient_mobile": doc.get("patient_mobile", ""),
        "date": app_date,
        "appointment_date": app_date,
        "slot": time_slot,
        "time_slot": time_slot,
        "reason": doc.get("reason", ""),
        "temperature": doc.get("temperature"),
        "symptoms": doc.get("symptoms", []),
        "notes": doc.get("notes", ""),
        "status": status,
        "created_at": doc.get("created_at", ""),
    }
