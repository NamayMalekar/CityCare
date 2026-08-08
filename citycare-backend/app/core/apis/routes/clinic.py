"""
Clinic routes — public endpoints for clinic info, hospitals, doctors, and free slots.
"""
from typing import Optional, List
from fastapi import APIRouter, Query

from app.controllers import clinic as clinic_controller
from app.core.apis.schemas.appointment import ClinicInfoOut, FreeSlotsOut
from app.core.apis.schemas.hospital import HospitalOut
from app.core.apis.schemas.doctor import DoctorOut

router = APIRouter(prefix="/clinic", tags=["clinic"])


@router.get("/info", response_model=ClinicInfoOut)
async def clinic_info():
    return clinic_controller.get_clinic_info()


@router.get("/free-slots", response_model=FreeSlotsOut)
async def free_slots(
    date: str = Query(..., description="YYYY-MM-DD"),
    doctor_id: Optional[str] = Query(None),
    hospital_id: Optional[str] = Query(None),
):
    return await clinic_controller.get_free_slots(date_str=date, doctor_id=doctor_id, hospital_id=hospital_id)


@router.get("/hospitals", response_model=List[HospitalOut])
async def list_hospitals():
    return await clinic_controller.list_hospitals()


@router.get("/doctors", response_model=List[DoctorOut])
async def list_doctors(
    hospital_id: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
):
    return await clinic_controller.list_doctors(hospital_id=hospital_id, specialization=specialization)
