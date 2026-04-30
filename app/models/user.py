"""
User model — shared by admin, doctor, and patient roles.
Handles authentication and role-based access control.
"""

from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login session management."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    Central user table for all roles: admin, doctor, patient.

    Attributes:
        id (int): Primary key.
        username (str): Unique login name.
        email (str): Unique email address.
        password_hash (str): Bcrypt-hashed password.
        role (str): One of 'admin', 'doctor', 'patient'.
        first_name (str): User's first name.
        last_name (str): User's last name.
        is_active (bool): Whether the account is enabled.
        created_at (datetime): Account creation timestamp.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="patient")  # admin | doctor | patient
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor_profile = db.relationship("Doctor", backref="user", uselist=False, lazy=True)
    patient_profile = db.relationship("Patient", backref="user", uselist=False, lazy=True)

    def set_password(self, password):
        """Hash and store the password using bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        """Return True if the user has admin role."""
        return self.role == "admin"

    def is_doctor(self):
        """Return True if the user has doctor role."""
        return self.role == "doctor"

    def is_patient(self):
        """Return True if the user has patient role."""
        return self.role == "patient"

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"
