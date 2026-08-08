"""
User schemas supporting Multi-Hospital System and Role-Based Access Control (RBAC).
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    mobile: str = Field(..., pattern=r"^(?:\+?91|0)?[6-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[str] = "PATIENT"
    hospital_id: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str
    role: str
    hospital_id: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    first_name: str
    hospital_id: Optional[str] = None
