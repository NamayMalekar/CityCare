"""
Patient routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_patient, get_current_user
from app.controllers import clinic as clinic_controller
from app.controllers import appointment as appt_controller
from app.core.apis.schemas.hospital import HospitalOut
from app.core.apis.schemas.doctor import DoctorOut
from app.core.apis.schemas.appointment import BookIn, AppointmentOut

router = APIRouter(prefix="/patient", tags=["patient"])


@router.get("/hospitals", response_model=List[HospitalOut])
async def list_hospitals():
    return await clinic_controller.list_hospitals()


@router.get("/doctors", response_model=List[DoctorOut])
async def list_doctors(
    hospital_id: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
):
    return await clinic_controller.list_doctors(hospital_id=hospital_id, specialization=specialization)


@router.post("/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    payload: BookIn,
    current_user: dict = Depends(get_current_user),
):
    return await appt_controller.book(current_user, payload)


@router.get("/appointments", response_model=List[AppointmentOut])
async def my_appointments(
    current_user: dict = Depends(get_current_user),
):
    return await appt_controller.my_appointments(current_user)
