"""
Super Admin controller.
"""
from fastapi import HTTPException, status
from app.core.cruds import hospital as hospital_crud
from app.core.cruds import doctor as doctor_crud
from app.core.cruds import appointment as appointment_crud
from app.core.cruds import user as user_crud
from app.core.security import hash_password
from app.core.models.user import user_public
from app.core.database import get_db


async def create_hospital(payload: dict) -> dict:
    return await hospital_crud.create_hospital(payload)


async def list_hospitals() -> list[dict]:
    return await hospital_crud.list_hospitals()


async def get_hospital(hospital_id: str) -> dict:
    hospital = await hospital_crud.get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return hospital


async def update_hospital(hospital_id: str, payload: dict) -> dict:
    updated = await hospital_crud.update_hospital(hospital_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return updated


async def delete_hospital(hospital_id: str) -> dict:
    success = await hospital_crud.delete_hospital(hospital_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return {"message": "Hospital deleted successfully"}


async def create_hospital_admin(payload: dict) -> dict:
    hospital = await hospital_crud.get_hospital(payload["hospital_id"])
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target hospital not found")

    hashed = hash_password(payload["password"])
    user = await user_crud.create_user(
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload["email"],
        mobile=payload["mobile"],
        hashed_password=hashed,
        role="HOSPITAL_ADMIN",
        hospital_id=payload["hospital_id"],
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    return user_public(user)


async def get_system_analytics() -> dict:
    db = get_db()
    total_hospitals = await db.hospitals.count_documents({})
    total_doctors = await db.doctors.count_documents({})
    total_appointments = await db.appointments.count_documents({})
    total_patients = await db.users.count_documents({"role": {"$in": ["patient", "PATIENT"]}})

    return {
        "total_hospitals": total_hospitals,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_patients": total_patients,
    }
