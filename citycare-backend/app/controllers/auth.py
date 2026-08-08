"""
Auth controller — signup and login logic.
"""
import logging
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token
from app.core.cruds import user as user_crud
from app.core.models.user import user_public
from app.core.apis.schemas.user import SignupIn, LoginIn

logger = logging.getLogger("citycare")


async def signup(payload: SignupIn) -> dict:
    hashed = hash_password(payload.password)
    # Public signup ALWAYS creates a patient (R8)
    role = "patient"

    created = await user_crud.create_user(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        mobile=payload.mobile,
        hashed_password=hashed,
        role=role,
        hospital_id=payload.hospital_id,
    )
    if created is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    logger.info("New user registered: %s (role=%s)", payload.email, role)
    return user_public(created)


async def login(payload: LoginIn) -> dict:
    user = await user_crud.get_user_by_email(payload.email)
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
    )
    if user is None:
        raise invalid
    if not verify_password(payload.password, user["password"]):
        raise invalid

    raw_role = user.get("role", "patient")
    role_str = str(raw_role).lower()
    hospital_id = str(user["hospital_id"]) if user.get("hospital_id") else None

    token = create_access_token(subject=str(user["_id"]), role=role_str, hospital_id=hospital_id)
    logger.info("Login success: %s (role=%s)", user["email"], role_str)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role_str,
        "first_name": user.get("first_name", ""),
        "hospital_id": hospital_id,
    }
