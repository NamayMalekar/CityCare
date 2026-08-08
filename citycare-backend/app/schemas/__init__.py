import sys
from app.core.apis.schemas import user, appointment, hospital, doctor

sys.modules['app.schemas.user'] = user
sys.modules['app.schemas.appointment'] = appointment
sys.modules['app.schemas.hospital'] = hospital
sys.modules['app.schemas.doctor'] = doctor

__all__ = ["user", "appointment", "hospital", "doctor"]
