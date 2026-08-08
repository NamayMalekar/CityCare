"""
Auth dependencies — RBAC authorization helpers and user verification.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

from app.core.security import decode_access_token
from app.core.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — please log in first.",
        )
    payload = decode_access_token(creds.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token — please log in again.",
        )

    user_id = payload["sub"]
    token_role = payload.get("role", "PATIENT").upper()
    token_hospital_id = payload.get("hospital_id")

    # Fetch latest user from DB if available for accurate role & hospital_id
    try:
        db = get_db()
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            db_role = (user_doc.get("role") or token_role).upper()
            hospital_id = str(user_doc.get("hospital_id")) if user_doc.get("hospital_id") else token_hospital_id
            return {
                "id": user_id,
                "role": db_role,
                "hospital_id": hospital_id,
                "first_name": user_doc.get("first_name", ""),
                "last_name": user_doc.get("last_name", ""),
                "email": user_doc.get("email", ""),
                "mobile": user_doc.get("mobile", ""),
            }
    except Exception:
        pass

    return {
        "id": user_id,
        "role": token_role,
        "hospital_id": token_hospital_id,
    }


async def require_super_admin(user: dict = Depends(get_current_user)) -> dict:
    """Authorization guard for SUPER_ADMIN role."""
    role = user["role"].upper()
    if role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied — Super Admin privileges required.",
        )
    return user


async def require_hospital_admin(user: dict = Depends(get_current_user)) -> dict:
    """Authorization guard for HOSPITAL_ADMIN role (or SUPER_ADMIN)."""
    role = user["role"].upper()
    if role not in ("HOSPITAL_ADMIN", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied — Hospital Admin privileges required.",
        )
    return user


async def require_doctor(user: dict = Depends(get_current_user)) -> dict:
    """Authorization guard for DOCTOR role."""
    role = user["role"].upper()
    if role not in ("DOCTOR", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may not access this — doctor only.",
        )
    return user


async def require_patient(user: dict = Depends(get_current_user)) -> dict:
    """Authorization guard for PATIENT role."""
    role = user["role"].upper()
    if role not in ("PATIENT", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied — Patient privileges required.",
        )
    return user
