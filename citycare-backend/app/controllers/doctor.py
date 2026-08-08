"""
Doctor controller — manages doctor dashboard, appointment statuses, and schedule.
"""
from fastapi import HTTPException, status
from app.core.cruds import doctor as doctor_crud
from app.core.cruds import appointment as appointment_crud
from app.core.cruds import user as user_crud
from app.core.models.appointment import appointment_for_doctor, appointment_public
from app.core.utils.dates import today_utc_date, parse_iso_date


async def list_doctor_appointments(current_user: dict, status_filter: str | None = None) -> list[dict]:
    # Resolve doctor_id for current user
    doctor = await doctor_crud.get_doctor_by_user_id(current_user["id"])
    if doctor:
        doctor_id = doctor["id"]
        docs = await appointment_crud.list_for_doctor(doctor_id, status=status_filter)
    else:
        # Fallback to general list if no doctor record bound
        docs = await appointment_crud.list_all_appointments(status=status_filter)
    return [appointment_for_doctor(d) for d in docs]


async def update_appointment_status(current_user: dict, appointment_id: str, new_status: str, notes: str | None = None) -> dict:
    appt = await appointment_crud.get_by_id(appointment_id)
    if appt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )

    updated = await appointment_crud.update_status(appointment_id, new_status, notes)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update appointment status.",
        )
    return appointment_for_doctor(updated)


async def get_doctor_dashboard_summary(current_user: dict) -> dict:
    doctor = await doctor_crud.get_doctor_by_user_id(current_user["id"])
    doctor_id = doctor["id"] if doctor else None
    today = today_utc_date().isoformat()

    all_appts = await appointment_crud.list_for_doctor(doctor_id) if doctor_id else await appointment_crud.list_all_appointments()

    pending_count = sum(1 for a in all_appts if a.get("status", "").upper() == "PENDING")
    today_count = sum(1 for a in all_appts if (a.get("date") == today or a.get("appointment_date") == today) and a.get("status", "").upper() in ("PENDING", "CONFIRMED", "BOOKED"))
    upcoming_count = sum(1 for a in all_appts if (a.get("date") or a.get("appointment_date") or "") > today and a.get("status", "").upper() in ("PENDING", "CONFIRMED", "BOOKED"))
    total_patients = await user_crud.count_patients()

    return {
        "pending_count": pending_count,
        "today_count": today_count,
        "upcoming_count": upcoming_count,
        "total_registered_patients": total_patients,
        "todays_visits": today_count,
        "upcoming_visits": upcoming_count,
    }


async def doctor_schedule(current_user: dict, date_str: str) -> dict:
    parsed_date = parse_iso_date(date_str)
    iso = parsed_date.isoformat()

    doctor = await doctor_crud.get_doctor_by_user_id(current_user["id"])
    doctor_id = doctor["id"] if doctor else None

    docs = await appointment_crud.list_for_date(iso, doctor_id=doctor_id)
    return {
        "date": iso,
        "schedule": [appointment_for_doctor(d) for d in docs],
    }


async def doctor_stats(current_user: dict) -> dict:
    return await get_doctor_dashboard_summary(current_user)
