"""
Appointment schemas supporting Multi-Hospital System.
"""
from typing import Optional, List
from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator


class BookIn(BaseModel):
    hospital_id: Optional[str] = None
    doctor_id: Optional[str] = None
    date: Optional[date_type] = None
    appointment_date: Optional[str] = None
    slot: Optional[str] = None
    time_slot: Optional[str] = None
    reason: str = Field(..., min_length=5, max_length=500)
    temperature: Optional[float] = Field(default=None, ge=95.0, le=110.0)
    symptoms: List[str] = Field(default_factory=list)
    notes: Optional[str] = ""

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Please provide a reason for the appointment.")
        return v


class AppointmentStatusUpdate(BaseModel):
    status: str = Field(..., description="PENDING, CONFIRMED, CANCELLED, COMPLETED")
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: str
    hospital_id: Optional[str] = None
    doctor_id: Optional[str] = None
    patient_id: Optional[str] = None
    date: str
    appointment_date: str
    slot: str
    time_slot: str
    reason: str
    temperature: Optional[float] = None
    symptoms: List[str] = Field(default_factory=list)
    notes: Optional[str] = ""
    status: str
    doctor_name: Optional[str] = ""
    hospital_name: Optional[str] = ""
    created_at: str


class DoctorScheduleItem(BaseModel):
    id: str
    hospital_id: Optional[str] = None
    doctor_id: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: str
    patient_email: Optional[str] = ""
    patient_mobile: Optional[str] = ""
    date: str
    appointment_date: str
    slot: str
    time_slot: str
    reason: str
    temperature: Optional[float] = None
    symptoms: List[str] = Field(default_factory=list)
    notes: Optional[str] = ""
    status: str
    created_at: str


class FreeSlotsOut(BaseModel):
    date: str
    free_slots: List[str]


class ClinicInfoOut(BaseModel):
    doctor_name: str
    qualification: str
    clinic_name: str
    address: str
    morning_hours: str
    evening_hours: str
    slot_length_minutes: int
    slots: List[str]


class DoctorStatsOut(BaseModel):
    total_registered_patients: int
    todays_visits: int
    upcoming_visits: int
    pending_count: Optional[int] = 0
    today_count: Optional[int] = 0
    upcoming_count: Optional[int] = 0


class MessageOut(BaseModel):
    message: str
