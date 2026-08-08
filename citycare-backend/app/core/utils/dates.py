"""
Date utilities — R4's four failure modes, in one place.

A date can be wrong in FOUR ways:
  1. not a real date at all / badly formatted  -> 422 (shape)
  2. in the past                               -> 400 (business)
  3. too far in the future                     -> 400 (business)

Everything here works in UTC (R10). "Today" is the UTC calendar date.
"""
from datetime import date as date_type, datetime, timezone

from fastapi import HTTPException, status

from app.core.config import BOOKING_WINDOW_DAYS


def today_utc_date() -> date_type:
    return datetime.now(timezone.utc).date()


def parse_iso_date(date_str: str) -> date_type:
    """Gate 2 slice: is this even a real, well-formatted date?"""
    try:
        return date_type.fromisoformat(date_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date format — expected YYYY-MM-DD.",
        )


def validate_booking_date(date_str: str) -> date_type:
    """
    Full check: format (Gate 2) + business window (Gate 3).
    Returns the parsed date if every check passes.
    """
    parsed = parse_iso_date(date_str)
    today = today_utc_date()

    if parsed < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That date is in the past. Please pick today or a later date.",
        )

    max_date = today.fromordinal(today.toordinal() + BOOKING_WINDOW_DAYS)
    if parsed > max_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bookings open only up to {BOOKING_WINDOW_DAYS} days ahead.",
        )
    return parsed
