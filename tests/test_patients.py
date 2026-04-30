"""
Unit and integration tests for patient management.
"""

from tests.conftest import login, logout
from app import db
from app.models.patient import Patient


class TestPatientDashboard:
    """Tests for the patient's personal dashboard."""

    def test_dashboard_requires_login(self, client):
        """Unauthenticated access should redirect to login."""
        resp = client.get("/patients/dashboard", follow_redirects=False)
        assert resp.status_code == 302

    def test_dashboard_loads_for_patient(self, client):
        """Patient dashboard should load and show the patient's name."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/patients/dashboard")
        assert resp.status_code == 200
        assert b"Jane" in resp.data
        logout(client)

    def test_dashboard_denied_to_admin(self, client):
        """Admin should not reach the patient dashboard."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/patients/dashboard", follow_redirects=False)
        assert resp.status_code in [302, 403]
        logout(client)


class TestPatientList:
    """Tests for the admin-only patient list page."""

    def test_patient_list_accessible_to_admin(self, client):
        """Admin should see the full patient list."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/patients/")
        assert resp.status_code == 200
        assert b"Doe" in resp.data
        logout(client)

    def test_patient_list_denied_to_patient(self, client):
        """Patients must not access the admin patient list."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/patients/", follow_redirects=False)
        assert resp.status_code in [302, 403]
        logout(client)

    def test_patient_search(self, client):
        """Admin search should filter patients correctly."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/patients/?q=Jane")
        assert resp.status_code == 200
        assert b"Jane" in resp.data
        logout(client)


class TestPatientProfile:
    """Tests for viewing and editing a patient profile."""

    def test_patient_can_view_own_profile(self, client, app):
        """A patient should be able to view their own profile."""
        with app.app_context():
            patient = Patient.query.first()
            pat_id = patient.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.get(f"/patients/{pat_id}")
        assert resp.status_code == 200
        assert b"Jane" in resp.data
        logout(client)

    def test_admin_can_view_any_patient(self, client, app):
        """Admin should be able to view any patient's profile."""
        with app.app_context():
            patient = Patient.query.first()
            pat_id = patient.id

        login(client, "admin@test.com", "Admin@1234")
        resp = client.get(f"/patients/{pat_id}")
        assert resp.status_code == 200
        logout(client)

    def test_patient_can_edit_own_profile(self, client, app):
        """A patient editing their own profile should persist changes."""
        with app.app_context():
            patient = Patient.query.first()
            pat_id = patient.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post(f"/patients/{pat_id}/edit", data={
            "first_name":        "Jane",
            "last_name":         "Doe",
            "gender":            "Female",
            "blood_type":        "A+",
            "phone":             "555-9999",
            "address":           "123 Main St",
            "emergency_contact": "John Doe — 555-1111",
            "medical_history":   "No known allergies.",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"updated" in resp.data.lower() or b"Jane" in resp.data

        with app.app_context():
            updated = Patient.query.get(pat_id)
            assert updated.phone == "555-9999"

        logout(client)

    def test_patient_cannot_view_other_patient(self, client, app):
        """A patient should not be able to view another patient's profile."""
        with app.app_context():
            # Create a second patient
            from app.models.user import User
            u2 = User(username="other", email="other@test.com",
                      first_name="Other", last_name="Patient", role="patient")
            u2.set_password("Other@1234")
            db.session.add(u2)
            db.session.flush()
            p2 = Patient(user_id=u2.id)
            db.session.add(p2)
            db.session.commit()
            other_id = p2.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.get(f"/patients/{other_id}", follow_redirects=False)
        assert resp.status_code in [302, 403]
        logout(client)
