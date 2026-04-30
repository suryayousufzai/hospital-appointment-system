"""
Models package — imports all models so SQLAlchemy can discover them.
"""

from app.models.user import User
from app.models.doctor import Doctor, Department
from app.models.patient import Patient
from app.models.appointment import Appointment
