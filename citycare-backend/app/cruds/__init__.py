import sys
from app.core.cruds import user, appointment, database, hospital, doctor

sys.modules['app.cruds.user'] = user
sys.modules['app.cruds.appointment'] = appointment
sys.modules['app.cruds.database'] = database
sys.modules['app.cruds.hospital'] = hospital
sys.modules['app.cruds.doctor'] = doctor

__all__ = ["user", "appointment", "database", "hospital", "doctor"]
