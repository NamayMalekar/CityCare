"""
Security primitives — password hashing and JWT token handling.
"""
import logging
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

logging.getLogger("passlib").setLevel(logging.CRITICAL)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str, hospital_id: str | None = None) -> str:
    """
    JWT Payload encodes user_id (`sub`), `role`, and `hospital_id` (if applicable).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    # Normalize role to uppercase representation
    norm_role = role.upper() if isinstance(role, str) else "PATIENT"

    payload = {
        "sub": subject,
        "role": norm_role,
        "hospital_id": hospital_id,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
