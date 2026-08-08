import sys
from app.core.models import user, appointment, hospital, doctor

sys.modules['app.models.user'] = user
sys.modules['app.models.appointment'] = appointment
sys.modules['app.models.hospital'] = hospital
sys.modules['app.models.doctor'] = doctor

__all__ = ["user", "appointment", "hospital", "doctor"]
