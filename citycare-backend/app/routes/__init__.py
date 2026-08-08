import sys
from app.core.apis.routes import auth, clinic, appointment, doctor, super_admin, hospital_admin, patient

sys.modules['app.routes.auth'] = auth
sys.modules['app.routes.clinic'] = clinic
sys.modules['app.routes.appointment'] = appointment
sys.modules['app.routes.doctor'] = doctor
sys.modules['app.routes.super_admin'] = super_admin
sys.modules['app.routes.hospital_admin'] = hospital_admin
sys.modules['app.routes.patient'] = patient

__all__ = ["auth", "clinic", "appointment", "doctor", "super_admin", "hospital_admin", "patient"]
