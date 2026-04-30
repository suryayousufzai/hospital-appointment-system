"""
Doctor and Department models.
A doctor belongs to a department and has a weekly availability schedule.
"""

from datetime import datetime
from app import db


class Department(db.Model):
    """
    Hospital department (e.g., Cardiology, Neurology).

    Attributes:
        id (int): Primary key.
        name (str): Department name (unique).
        description (str): Optional description.
    """

    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    doctors = db.relationship("Doctor", backref="department", lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"


class Doctor(db.Model):
    """
    Doctor profile linked to a User account.

    Attributes:
        id (int): Primary key.
        user_id (int): FK → users.id.
        department_id (int): FK → departments.id.
        specialty (str): Medical specialty.
        phone (str): Contact phone number.
        bio (str): Short professional biography.
        availability (str): JSON string of available days/hours.
        consultation_fee (float): Fee per appointment (in USD).
        is_available (bool): Whether the doctor is currently accepting patients.
        created_at (datetime): Profile creation timestamp.
    """

    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    # Stored as comma-separated days: "Monday,Wednesday,Friday"
    available_days = db.Column(db.String(100), nullable=True, default="Monday,Wednesday,Friday")
    available_from = db.Column(db.String(5), nullable=True, default="09:00")   # HH:MM
    available_to = db.Column(db.String(5), nullable=True, default="17:00")     # HH:MM
    consultation_fee = db.Column(db.Float, nullable=False, default=0.0)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship("Appointment", backref="doctor", lazy=True)

    @property
    def available_days_list(self):
        """Return available days as a Python list."""
        if self.available_days:
            return [day.strip() for day in self.available_days.split(",")]
        return []

    def __repr__(self):
        return f"<Doctor {self.user.full_name} — {self.specialty}>"
