"""
Appointment routes — the protected patient endpoints.

Every route here depends on get_current_user (Gate 1). Identity is taken from
that dependency, never from the request body (R7).
"""
from fastapi import APIRouter, Depends, status

from app.controllers import appointment as appt_controller
from app.core.deps import get_current_user
from app.schemas.appointment import BookIn, AppointmentOut, MessageOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def book(payload: BookIn, current_user: dict = Depends(get_current_user)):
    return await appt_controller.book(current_user, payload)


@router.get("/mine", response_model=list[AppointmentOut])
async def my_appointments(current_user: dict = Depends(get_current_user)):
    return await appt_controller.my_appointments(current_user)


@router.patch("/{appointment_id}/cancel", response_model=MessageOut)
async def cancel(appointment_id: str, current_user: dict = Depends(get_current_user)):
    return await appt_controller.cancel(current_user, appointment_id)
