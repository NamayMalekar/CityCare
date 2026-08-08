"""
Configuration — R2 in the brief: "model today's truth, not tomorrow's maybe."

There is ONE doctor and ONE clinic. That is a FACT THAT NEVER CHANGES, so it
lives here in configuration, NOT in a database collection. Making it a
collection would be the "simple projects grow tumors" mistake the brief warns
about.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "citycare"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()

# ── The clinic is configuration, not data (R2) ───────────────────────────────
CLINIC_INFO = {
    "doctor_name": "Dr. Meera Kulkarni",
    "qualification": "MBBS, MD — General Physician",
    "clinic_name": "CityCare Clinic",
    "address": "Dharampeth, Nagpur",
    "morning_hours": "10:00–13:00",
    "evening_hours": "17:00–20:00",
    "slot_length_minutes": 30,
}

# ── The fixed menu of exactly 12 slots (R3) ──────────────────────────────────
# The hours + 30-minute rule SECRETLY DEFINE these. Free slots are never stored;
# they are calculated fresh every time as (this menu) minus (booked for a date).
# Morning 10:00–13:00 -> 6 slots. Evening 17:00–20:00 -> 6 slots. Total 12.
def _build_slots() -> list[str]:
    slots: list[str] = []
    for start_hour, end_hour in [(10, 13), (17, 20)]:
        hour, minute = start_hour, 0
        while hour < end_hour:
            slots.append(f"{hour:02d}:{minute:02d}")
            minute += 30
            if minute == 60:
                minute = 0
                hour += 1
    return slots


ALL_SLOTS: list[str] = _build_slots()  # ['10:00', '10:30', ... '19:30'] -> 12

# ── The booking window (R4) ──────────────────────────────────────────────────
BOOKING_WINDOW_DAYS = 7  # today up to 7 days ahead
