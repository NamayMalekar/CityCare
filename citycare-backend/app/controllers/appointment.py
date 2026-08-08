"""
Appointment controller — handles booking, listing patient appointments, and cancellation.
"""
import logging
from fastapi import HTTPException, status

from app.core.config import ALL_SLOTS
from app.core.cruds import appointment as appt_crud
from app.core.cruds import user as user_crud
from app.core.models.appointment import appointment_public
from app.core.apis.schemas.appointment import BookIn
from app.core.utils.dates import validate_booking_date

logger = logging.getLogger("citycare")


async def book(current_user: dict, payload: BookIn) -> dict:
    patient_id = current_user["id"]

    # Support date / appointment_date and slot / time_slot
    raw_date = payload.appointment_date or (payload.date.isoformat() if payload.date else None)
    if not raw_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date is required.",
        )
    raw_slot = payload.time_slot or payload.slot
    if not raw_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot is required.",
        )

    parsed = validate_booking_date(raw_date)
    iso = parsed.isoformat()

    if raw_slot not in ALL_SLOTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That slot is not on the clinic's schedule.",
        )

    # Check free slots for doctor/hospital if specified
    booked = set(await appt_crud.booked_slots_for_date(iso, doctor_id=payload.doctor_id, hospital_id=payload.hospital_id))
    if raw_slot in booked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That slot just got booked — please pick another.",
        )

    user = await user_crud.get_user_by_id(patient_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account could not be found — please log in again.",
        )
    patient_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()

    try:
        doc = await appt_crud.insert_booking(
            patient_id=patient_id,
            patient_name=patient_name,
            date_str=iso,
            slot=raw_slot,
            reason=payload.reason,
            temperature=payload.temperature,
            symptoms=[s.value if hasattr(s, 'value') else str(s) for s in payload.symptoms],
            hospital_id=payload.hospital_id,
            doctor_id=payload.doctor_id,
            notes=payload.notes,
            status="PENDING",
        )
    except appt_crud.SlotTakenError:
        logger.info("Steel door refused a double-book: %s %s", iso, raw_slot)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That slot just got booked — please pick another.",
        )

    logger.info("Booking submitted: patient=%s %s %s", patient_id, iso, raw_slot)
    return appointment_public(doc)


async def my_appointments(current_user: dict) -> list[dict]:
    docs = await appt_crud.list_for_patient(current_user["id"])
    return [appointment_public(d) for d in docs]


async def cancel(current_user: dict, appointment_id: str) -> dict:
    appt = await appt_crud.get_by_id(appointment_id)
    if appt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )
    if appt["patient_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may not cancel an appointment that isn't yours.",
        )
    if (appt.get("status") or "").upper() == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This appointment is already cancelled.",
        )
    ok = await appt_crud.cancel(appointment_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This appointment is already cancelled.",
        )
    logger.info("Appointment cancelled: %s by %s", appointment_id, current_user["id"])
    return {"message": "Appointment cancelled — the slot is free again."}
