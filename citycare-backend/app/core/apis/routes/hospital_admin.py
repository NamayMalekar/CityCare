"""
Hospital Admin routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status

from app.core.deps import require_hospital_admin
from app.controllers import hospital_admin as hospital_admin_controller
from app.core.apis.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorOut
from app.core.apis.schemas.appointment import AppointmentOut

router = APIRouter(prefix="/hospital-admin", tags=["hospital-admin"])


@router.post("/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def onboard_doctor(
    payload: DoctorCreate,
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.onboard_doctor(current_user, payload.model_dump())


@router.get("/doctors", response_model=List[DoctorOut])
async def list_doctors(
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.list_hospital_doctors(current_user)


@router.put("/doctors/{doctor_id}", response_model=DoctorOut)
async def update_doctor(
    doctor_id: str,
    payload: DoctorUpdate,
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.update_doctor(doctor_id, payload.model_dump(exclude_unset=True))


@router.delete("/doctors/{doctor_id}")
async def delete_doctor(
    doctor_id: str,
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.delete_doctor(doctor_id)


@router.get("/appointments")
async def list_hospital_appointments(
    status: Optional[str] = None,
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.list_hospital_appointments(current_user, status_filter=status)


@router.get("/analytics")
@router.get("/stats")
async def get_hospital_analytics(
    current_user: dict = Depends(require_hospital_admin),
):
    return await hospital_admin_controller.get_hospital_analytics(current_user)
