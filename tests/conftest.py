"""
Pytest configuration and shared fixtures for the Hospital System test suite.
"""

import pytest
from app import create_app, db
from app.models.user import User
from app.models.doctor import Doctor, Department
from app.models.patient import Patient
from app.models.appointment import Appointment
from datetime import date


@pytest.fixture(scope="session")
def app():
    """Create a test application instance with in-memory SQLite database."""
    application = create_app("testing")
    return application


@pytest.fixture(scope="function")
def client(app):
    """Provide a fresh test client for each test (prevents session leakage)."""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Reset the database before each test for full isolation."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        _seed_test_data()
    yield
    with app.app_context():
        db.session.remove()


def _seed_test_data():
    """Create a minimal set of records shared across tests."""
    # Admin
    admin = User(username="admin", email="admin@test.com",
                 first_name="Admin", last_name="User", role="admin")
    admin.set_password("Admin@1234")
    db.session.add(admin)

    # Department
    dept = Department(name="Cardiology", description="Heart specialists")
    db.session.add(dept)
    db.session.flush()

    # Doctor user + profile
    doc_user = User(username="drsmith", email="drsmith@test.com",
                    first_name="John", last_name="Smith", role="doctor")
    doc_user.set_password("Doctor@1234")
    db.session.add(doc_user)
    db.session.flush()

    doctor = Doctor(
        user_id=doc_user.id, department_id=dept.id,
        specialty="Cardiologist", consultation_fee=150.0,
        available_days="Monday,Wednesday,Friday",
        available_from="09:00", available_to="17:00",
    )
    db.session.add(doctor)

    # Patient user + profile
    pat_user = User(username="janedoe", email="jane@test.com",
                    first_name="Jane", last_name="Doe", role="patient")
    pat_user.set_password("Patient@1234")
    db.session.add(pat_user)
    db.session.flush()

    patient = Patient(user_id=pat_user.id, phone="555-1234", blood_type="A+")
    db.session.add(patient)
    db.session.flush()

    # One appointment
    appt = Appointment(
        patient_id=patient.id, doctor_id=doctor.id,
        appointment_date=date(2026, 6, 15),
        appointment_time="10:00", status="pending",
        reason="Routine checkup"
    )
    db.session.add(appt)
    db.session.commit()


def login(client, email, password):
    """Helper: log in via the test client."""
    return client.post("/login", data={"email": email, "password": password},
                       follow_redirects=True)


def logout(client):
    """Helper: log out via the test client."""
    return client.get("/logout", follow_redirects=True)
