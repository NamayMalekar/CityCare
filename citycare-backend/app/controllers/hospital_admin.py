"""
Hospital Admin controller.
"""
from fastapi import HTTPException, status
from app.core.cruds import doctor as doctor_crud
from app.core.cruds import appointment as appointment_crud
from app.core.cruds import hospital as hospital_crud
from app.core.database import get_db


async def onboard_doctor(hospital_admin_user: dict, payload: dict) -> dict:
    hospital_id = hospital_admin_user.get("hospital_id") or payload.get("hospital_id")
    if not hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital ID is required for doctor onboarding.",
        )
    payload["hospital_id"] = hospital_id
    try:
        return await doctor_crud.create_doctor(payload)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err) or "Failed to onboard doctor.",
        )


async def list_hospital_doctors(hospital_admin_user: dict) -> list[dict]:
    hospital_id = hospital_admin_user.get("hospital_id")
    if not hospital_id:
        # If Super Admin or unassigned admin calls this, list all or empty
        return await doctor_crud.list_doctors()
    return await doctor_crud.list_doctors(hospital_id=hospital_id)


async def update_doctor(doctor_id: str, payload: dict) -> dict:
    updated = await doctor_crud.update_doctor(doctor_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return updated


async def delete_doctor(doctor_id: str) -> dict:
    success = await doctor_crud.delete_doctor(doctor_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return {"message": "Doctor deleted successfully"}


async def list_hospital_appointments(hospital_admin_user: dict, status_filter: str | None = None) -> list[dict]:
    hospital_id = hospital_admin_user.get("hospital_id")
    if not hospital_id:
        return await appointment_crud.list_all_appointments(status=status_filter)
    return await appointment_crud.list_for_hospital(hospital_id=hospital_id, status=status_filter)


async def get_hospital_analytics(hospital_admin_user: dict) -> dict:
    hospital_id = hospital_admin_user.get("hospital_id")
    db = get_db()
    if not hospital_id:
        total_doctors = await db.doctors.count_documents({})
        total_appointments = await db.appointments.count_documents({})
        pending_appointments = await db.appointments.count_documents({"status": "PENDING"})
        completed_appointments = await db.appointments.count_documents({"status": "COMPLETED"})
    else:
        from bson import ObjectId
        h_id_str = str(hospital_id)
        try:
            h_id_oid = ObjectId(hospital_id)
            doc_query = {"$or": [{"hospital_id": h_id_str}, {"hospital_id": h_id_oid}]}
        except Exception:
            doc_query = {"hospital_id": h_id_str}

        total_doctors = await db.doctors.count_documents(doc_query)
        total_appointments = await db.appointments.count_documents({"hospital_id": h_id_str})
        pending_appointments = await db.appointments.count_documents({"hospital_id": h_id_str, "status": "PENDING"})
        completed_appointments = await db.appointments.count_documents({"hospital_id": h_id_str, "status": "COMPLETED"})

    return {
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
    }
