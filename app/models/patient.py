"""
Patient model — stores medical and contact info for patients.
"""

from datetime import datetime
from app import db


class Patient(db.Model):
    """
    Patient profile linked to a User account.

    Attributes:
        id (int): Primary key.
        user_id (int): FK → users.id.
        date_of_birth (date): Patient's date of birth.
        gender (str): 'Male', 'Female', or 'Other'.
        blood_type (str): e.g., 'A+', 'O-'.
        phone (str): Contact phone number.
        address (str): Home address.
        emergency_contact (str): Emergency contact name and phone.
        medical_history (str): Free-text medical history notes.
        created_at (datetime): Profile creation timestamp.
    """

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male | Female | Other
    blood_type = db.Column(db.String(5), nullable=True)  # A+, O-, etc.
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    emergency_contact = db.Column(db.String(150), nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship("Appointment", backref="patient", lazy=True)

    @property
    def age(self):
        """Calculate the patient's current age in years."""
        if self.date_of_birth:
            today = datetime.today().date()
            dob = self.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    def __repr__(self):
        return f"<Patient {self.user.full_name}>"
