"""
Appointment model — core of the hospital booking system.
"""

from datetime import datetime
from app import db


class Appointment(db.Model):
    """
    Appointment record linking a patient to a doctor at a specific time.

    Statuses:
        pending   → Booked, awaiting confirmation
        confirmed → Confirmed by doctor/admin
        completed → Appointment took place
        cancelled → Cancelled by patient, doctor, or admin

    Attributes:
        id (int): Primary key.
        patient_id (int): FK → patients.id.
        doctor_id (int): FK → doctors.id.
        appointment_date (date): Date of the appointment.
        appointment_time (str): Time slot e.g. '10:00'.
        status (str): Current status of the appointment.
        reason (str): Patient's reason for visit.
        notes (str): Doctor's notes after the visit.
        created_at (datetime): When the booking was made.
        updated_at (datetime): Last time the record was modified.
    """

    __tablename__ = "appointments"

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    ALL_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_COMPLETED, STATUS_CANCELLED]

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(5), nullable=False)  # HH:MM format
    status = db.Column(db.String(20), nullable=False, default="pending")
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)   # Doctor fills this after visit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_upcoming(self):
        """Return True if the appointment is in the future."""
        return self.appointment_date >= datetime.today().date()

    @property
    def status_badge(self):
        """Return a Bootstrap badge color class based on status."""
        return {
            "pending": "warning",
            "confirmed": "primary",
            "completed": "success",
            "cancelled": "danger",
        }.get(self.status, "secondary")

    def __repr__(self):
        return (
            f"<Appointment #{self.id} | "
            f"Patient {self.patient_id} → Doctor {self.doctor_id} | "
            f"{self.appointment_date} {self.appointment_time} [{self.status}]>"
        )
