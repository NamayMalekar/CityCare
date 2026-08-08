"""
Database connection and unique index setup.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from app.core.config import settings

logger = logging.getLogger("citycare")

client: AsyncIOMotorClient | None = None


def get_db():
    return client[settings.db_name]


async def connect_to_mongo() -> None:
    global client
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]

    try:
        await db.users.create_index([("email", ASCENDING)], unique=True)
    except Exception:
        pass

    try:
        await db.appointments.create_index(
            [("date", ASCENDING), ("slot", ASCENDING)],
            unique=True,
            partialFilterExpression={"status": {"$in": ["booked", "PENDING", "CONFIRMED", "pending", "confirmed"]}},
            name="uniq_active_slot_per_date",
        )
    except Exception as err:
        logger.warning("Could not create uniq_active_slot_per_date index immediately: %s", err)

    logger.info("Connected to Mongo and ensured indexes.")


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()
        logger.info("Closed Mongo connection.")
