"""
Hospital Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class HospitalCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=3, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    contact_phone: str = Field(..., min_length=7, max_length=20)
    email: EmailStr


class HospitalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, min_length=3, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=50)
    contact_phone: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None


class HospitalOut(BaseModel):
    id: str
    name: str
    address: str
    city: str
    contact_phone: str
    email: str
    created_at: str


class HospitalAdminCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    hospital_id: str
