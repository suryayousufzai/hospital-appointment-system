"""
Unit and integration tests for doctor management.
"""

from tests.conftest import login, logout
from app import db
from app.models.doctor import Doctor, Department
from app.models.user import User


class TestDoctorList:
    """Tests for the public doctor listing page."""

    def test_doctor_list_requires_login(self, client):
        """Unauthenticated access should redirect to login."""
        resp = client.get("/doctors/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_doctor_list_loads_for_patient(self, client):
        """Patients should be able to view the doctor list."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/doctors/")
        assert resp.status_code == 200
        assert b"Smith" in resp.data
        logout(client)

    def test_doctor_list_loads_for_admin(self, client):
        """Admins should see the doctor list with an 'Add Doctor' button."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/doctors/")
        assert resp.status_code == 200
        assert b"Add Doctor" in resp.data
        logout(client)

    def test_doctor_search_by_name(self, client):
        """Search by name should return matching results."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/doctors/?q=Smith")
        assert resp.status_code == 200
        assert b"Smith" in resp.data
        logout(client)

    def test_doctor_search_no_results(self, client):
        """Search with no matches should show empty state."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/doctors/?q=zzznomatch")
        assert resp.status_code == 200
        logout(client)


class TestDoctorProfile:
    """Tests for viewing a doctor's profile page."""

    def test_view_doctor_profile(self, client, app):
        """Any logged-in user can view a doctor profile."""
        with app.app_context():
            doctor = Doctor.query.first()
            doc_id = doctor.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.get(f"/doctors/{doc_id}")
        assert resp.status_code == 200
        assert b"Smith" in resp.data
        logout(client)

    def test_view_nonexistent_doctor_returns_404(self, client):
        """Requesting a non-existent doctor should return 404."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/doctors/99999")
        assert resp.status_code == 404
        logout(client)


class TestAddDoctor:
    """Tests for admin adding a new doctor."""

    def test_add_doctor_page_accessible_to_admin(self, client):
        """Admin should reach the add doctor form."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/admin/doctors/add")
        assert resp.status_code == 200
        logout(client)

    def test_add_doctor_denied_to_patient(self, client):
        """Patients should not access the add doctor page."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/admin/doctors/add", follow_redirects=False)
        assert resp.status_code in [302, 403]
        logout(client)

    def test_add_doctor_creates_record(self, client, app):
        """Submitting valid data should create a doctor + user in the DB."""
        with app.app_context():
            dept_id = Department.query.first().id

        login(client, "admin@test.com", "Admin@1234")
        resp = client.post("/admin/doctors/add", data={
            "first_name":       "Alice",
            "last_name":        "Brown",
            "username":         "drbrown",
            "email":            "drbrown@test.com",
            "password":         "Doctor@1234",
            "specialty":        "Neurologist",
            "department_id":    dept_id,
            "consultation_fee": 200,
            "available_days":   "Tuesday,Thursday",
            "available_from":   "09:00",
            "available_to":     "16:00",
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            user = User.query.filter_by(email="drbrown@test.com").first()
            assert user is not None
            assert user.role == "doctor"
            assert user.doctor_profile is not None

        logout(client)


class TestEditDoctor:
    """Tests for editing a doctor's profile."""

    def test_doctor_can_edit_own_profile(self, client, app):
        """A doctor should be able to edit their own profile."""
        with app.app_context():
            doctor = Doctor.query.first()
            doc_id = doctor.id
            dept_id = doctor.department_id

        login(client, "drsmith@test.com", "Doctor@1234")
        resp = client.post(f"/doctors/{doc_id}/edit", data={
            "first_name":       "John",
            "last_name":        "Smith",
            "specialty":        "Senior Cardiologist",
            "department_id":    dept_id,
            "consultation_fee": 175,
            "available_from":   "09:00",
            "available_to":     "17:00",
            "available_days":   "Monday,Wednesday,Friday",
            "is_available":     "y",
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            updated = Doctor.query.get(doc_id)
            assert updated.specialty == "Senior Cardiologist"

        logout(client)
