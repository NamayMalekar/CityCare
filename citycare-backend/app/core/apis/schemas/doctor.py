"""
Doctor Pydantic schemas.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class DoctorCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    hospital_id: Optional[str] = None
    specialization: str = Field("General Medicine", min_length=2)
    qualification: str = Field("MBBS", min_length=2)
    consultation_fee: float = Field(500.0, ge=0)
    bio: Optional[str] = ""
    available_days: List[str] = Field(default_factory=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    available_days: Optional[List[str]] = None


class DoctorOut(BaseModel):
    id: str
    user_id: str
    hospital_id: str
    hospital_name: Optional[str] = ""
    first_name: str
    last_name: str
    name: str
    email: str
    mobile: str
    specialization: str
    qualification: str
    consultation_fee: float
    bio: str
    available_days: List[str]
