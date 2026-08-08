"""
Super Admin routes.
"""
from typing import List
from fastapi import APIRouter, Depends, status

from app.core.deps import require_super_admin
from app.controllers import super_admin as super_admin_controller
from app.core.apis.schemas.hospital import HospitalCreate, HospitalUpdate, HospitalOut, HospitalAdminCreate
from app.core.apis.schemas.user import UserOut

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


@router.post("/hospitals", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    payload: HospitalCreate,
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.create_hospital(payload.model_dump())


@router.get("/hospitals", response_model=List[HospitalOut])
async def list_hospitals(
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.list_hospitals()


@router.get("/hospitals/{hospital_id}", response_model=HospitalOut)
async def get_hospital(
    hospital_id: str,
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.get_hospital(hospital_id)


@router.put("/hospitals/{hospital_id}", response_model=HospitalOut)
async def update_hospital(
    hospital_id: str,
    payload: HospitalUpdate,
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.update_hospital(hospital_id, payload.model_dump(exclude_unset=True))


@router.delete("/hospitals/{hospital_id}")
async def delete_hospital(
    hospital_id: str,
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.delete_hospital(hospital_id)


@router.post("/hospital-admins", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_hospital_admin(
    payload: HospitalAdminCreate,
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.create_hospital_admin(payload.model_dump())


@router.get("/analytics")
@router.get("/stats")
async def get_analytics(
    current_user: dict = Depends(require_super_admin),
):
    return await super_admin_controller.get_system_analytics()
