"""
Seed the ONE doctor account (R8).

Public signup can never create a doctor, so we create the doctor here, by hand,
at setup time: sign her up like any user, then flip her role to "doctor"
directly in the database. Run once after Mongo is up:

    python seed_doctor.py

Idempotent — re-running just ensures the account exists with the doctor role.
"""
import asyncio
import logging

from app.core.database import connect_to_mongo, close_mongo_connection, get_db
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("citycare.seed")

DOCTOR_EMAIL = "dr.meera@citycare.clinic"
DOCTOR_PASSWORD = "doctor123"  # change after first login in a real deployment


async def main() -> None:
    await connect_to_mongo()
    db = get_db()

    existing = await db.users.find_one({"email": DOCTOR_EMAIL})
    if existing is None:
        await db.users.insert_one(
            {
                "first_name": "Meera",
                "last_name": "Kulkarni",
                "email": DOCTOR_EMAIL,
                "mobile": "+919999999999",
                "password": hash_password(DOCTOR_PASSWORD),
                "role": "doctor",  # the flip — done by the server, not a form
            }
        )
        logger.info("Doctor account created: %s", DOCTOR_EMAIL)
    else:
        # Ensure the role is correct even if it was created via public signup.
        await db.users.update_one(
            {"email": DOCTOR_EMAIL}, {"$set": {"role": "doctor"}}
        )
        logger.info("Doctor account already existed — role ensured as 'doctor'.")

    print("\n  Doctor login:")
    print(f"    email:    {DOCTOR_EMAIL}")
    print(f"    password: {DOCTOR_PASSWORD}\n")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
