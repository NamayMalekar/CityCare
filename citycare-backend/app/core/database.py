"""
Compatibility shim: expose the database helpers at
`app.core.database` while the implementation lives in `app.core.cruds.database`.
This keeps existing imports working without changing many files.
"""
from app.core.cruds.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_db,
)

__all__ = ["connect_to_mongo", "close_mongo_connection", "get_db"]
