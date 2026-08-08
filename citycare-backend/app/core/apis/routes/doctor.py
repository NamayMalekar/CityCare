"""
Doctor routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_doctor
from app.controllers import doctor as doctor_controller
from app.core.apis.schemas.appointment import DoctorScheduleItem, DoctorStatsOut, AppointmentStatusUpdate

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get("/appointments")
async def list_appointments(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, CONFIRMED, CANCELLED, COMPLETED)"),
    current_user: dict = Depends(require_doctor),
):
    return await doctor_controller.list_doctor_appointments(current_user, status_filter=status)


@router.patch("/appointments/{appointment_id}/status")
@router.patch("/appointments/{appointment_id}")
async def update_appointment_status(
    appointment_id: str,
    payload: AppointmentStatusUpdate,
    current_user: dict = Depends(require_doctor),
):
    return await doctor_controller.update_appointment_status(
        current_user=current_user,
        appointment_id=appointment_id,
        new_status=payload.status,
        notes=payload.notes,
    )


@router.get("/schedule")
async def schedule(
    date: str = Query(..., description="YYYY-MM-DD date"),
    current_user: dict = Depends(require_doctor),
):
    return await doctor_controller.doctor_schedule(current_user, date)


@router.get("/stats")
@router.get("/dashboard-summary")
async def stats(
    current_user: dict = Depends(require_doctor),
):
    return await doctor_controller.doctor_stats(current_user)
