"""
Clinic controller — open read endpoints for clinic info, hospitals, doctors, and free slots.
"""
from datetime import date as date_type
from fastapi import HTTPException, status

from app.core.config import CLINIC_INFO, ALL_SLOTS
from app.core.cruds import appointment as appt_crud
from app.core.cruds import hospital as hospital_crud
from app.core.cruds import doctor as doctor_crud
from app.core.utils.dates import validate_booking_date


def get_clinic_info() -> dict:
    return {**CLINIC_INFO, "slots": ALL_SLOTS}


async def get_free_slots(date_str: str, doctor_id: str | None = None, hospital_id: str | None = None) -> dict:
    parsed: date_type = validate_booking_date(date_str)
    iso = parsed.isoformat()

    booked = set(await appt_crud.booked_slots_for_date(iso, doctor_id=doctor_id, hospital_id=hospital_id))
    free = [s for s in ALL_SLOTS if s not in booked]
    return {"date": iso, "free_slots": free}


async def list_hospitals() -> list[dict]:
    return await hospital_crud.list_hospitals()


async def list_doctors(hospital_id: str | None = None, specialization: str | None = None) -> list[dict]:
    return await doctor_crud.list_doctors(hospital_id=hospital_id, specialization=specialization)
