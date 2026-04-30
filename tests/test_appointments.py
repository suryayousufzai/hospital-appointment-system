"""
Unit and integration tests for the appointment system.
"""

from datetime import date, timedelta
from tests.conftest import login, logout
from app import db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient


def future_date(days=10):
    """Return an ISO date string N days in the future."""
    return (date.today() + timedelta(days=days)).isoformat()


class TestAppointmentList:
    """Tests for the appointment list page."""

    def test_list_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        resp = client.get("/appointments/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_patient_sees_own_appointments(self, client):
        """Patient sees only their own appointments."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/appointments/")
        assert resp.status_code == 200
        assert b"appointment" in resp.data.lower()
        logout(client)

    def test_admin_sees_all_appointments(self, client):
        """Admin sees all appointments."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/appointments/")
        assert resp.status_code == 200
        logout(client)

    def test_filter_by_status(self, client):
        """Status filter should restrict results."""
        login(client, "admin@test.com", "Admin@1234")
        resp = client.get("/appointments/?status=pending")
        assert resp.status_code == 200
        logout(client)


class TestBookAppointment:
    """Tests for the appointment booking flow."""

    def test_book_page_loads_for_patient(self, client):
        """Patient should see the booking form."""
        login(client, "jane@test.com", "Patient@1234")
        resp = client.get("/appointments/book")
        assert resp.status_code == 200
        assert b"Book" in resp.data
        logout(client)

    def test_book_denied_to_doctor(self, client):
        """Doctors cannot access the booking page as bookers."""
        login(client, "drsmith@test.com", "Doctor@1234")
        resp = client.get("/appointments/book", follow_redirects=True)
        assert resp.status_code == 200
        logout(client)

    def test_patient_can_book_appointment(self, client, app):
        """Patient submitting valid booking data creates an appointment."""
        with app.app_context():
            doctor = Doctor.query.first()
            doc_id = doctor.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post("/appointments/book", data={
            "doctor_id":        doc_id,
            "appointment_date": future_date(7),
            "appointment_time": "11:00",
            "reason":           "Annual health checkup",
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            appts = Appointment.query.filter_by(appointment_time="11:00").all()
            assert any(a.reason == "Annual health checkup" for a in appts)

        logout(client)

    def test_cannot_book_past_date(self, client, app):
        """Booking in the past should show a warning."""
        with app.app_context():
            doc_id = Doctor.query.first().id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post("/appointments/book", data={
            "doctor_id":        doc_id,
            "appointment_date": "2020-01-01",
            "appointment_time": "09:00",
            "reason":           "Past booking attempt",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"past" in resp.data.lower() or b"Cannot" in resp.data

        logout(client)

    def test_duplicate_booking_prevented(self, client, app):
        """Booking the same doctor/date/time slot twice should show a warning."""
        with app.app_context():
            doc_id  = Doctor.query.first().id
            pat_id  = Patient.query.first().id
            appt = Appointment(
                doctor_id=doc_id, patient_id=pat_id,
                appointment_date=date.today() + timedelta(days=5),
                appointment_time="14:00", status="pending"
            )
            db.session.add(appt)
            db.session.commit()
            booked_date = appt.appointment_date.isoformat()

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post("/appointments/book", data={
            "doctor_id":        doc_id,
            "appointment_date": booked_date,
            "appointment_time": "14:00",
            "reason":           "Duplicate slot",
        }, follow_redirects=True)
        assert b"already booked" in resp.data.lower() or b"slot" in resp.data.lower()
        logout(client)


class TestViewAppointment:
    """Tests for viewing a single appointment."""

    def test_patient_can_view_own_appointment(self, client, app):
        """Patient should see their appointment detail page."""
        with app.app_context():
            appt = Appointment.query.first()
            appt_id = appt.id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.get(f"/appointments/{appt_id}")
        assert resp.status_code == 200
        logout(client)

    def test_doctor_can_view_their_appointment(self, client, app):
        """Doctor should see appointments assigned to them."""
        with app.app_context():
            appt_id = Appointment.query.first().id

        login(client, "drsmith@test.com", "Doctor@1234")
        resp = client.get(f"/appointments/{appt_id}")
        assert resp.status_code == 200
        logout(client)


class TestUpdateAppointment:
    """Tests for updating appointment status."""

    def test_doctor_can_confirm_appointment(self, client, app):
        """Doctor should be able to confirm a pending appointment."""
        with app.app_context():
            appt_id = Appointment.query.first().id

        login(client, "drsmith@test.com", "Doctor@1234")
        resp = client.post(f"/appointments/{appt_id}/update", data={
            "status": "confirmed",
            "notes":  "Confirmed — please bring previous test results.",
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            updated = Appointment.query.get(appt_id)
            assert updated.status == "confirmed"

        logout(client)

    def test_patient_cannot_update_status(self, client, app):
        """Patients should not be able to update appointment status."""
        with app.app_context():
            appt_id = Appointment.query.first().id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post(f"/appointments/{appt_id}/update", data={
            "status": "completed",
            "notes":  "Unauthorized update",
        }, follow_redirects=True)
        # Should be redirected away, not process the update
        with app.app_context():
            appt = Appointment.query.get(appt_id)
            assert appt.status != "completed"

        logout(client)


class TestCancelAppointment:
    """Tests for cancelling appointments."""

    def test_patient_can_cancel_own_appointment(self, client, app):
        """Patient should be able to cancel their pending appointment."""
        with app.app_context():
            appt_id = Appointment.query.first().id

        login(client, "jane@test.com", "Patient@1234")
        resp = client.post(f"/appointments/{appt_id}/cancel",
                           follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            cancelled = Appointment.query.get(appt_id)
            assert cancelled.status == "cancelled"

        logout(client)

    def test_cannot_cancel_completed_appointment(self, client, app):
        """A completed appointment should not be cancellable."""
        with app.app_context():
            appt = Appointment.query.first()
            appt.status = "completed"
            db.session.commit()
            appt_id = appt.id

        login(client, "jane@test.com", "Patient@1234")
        client.post(f"/appointments/{appt_id}/cancel", follow_redirects=True)

        with app.app_context():
            appt = Appointment.query.get(appt_id)
            assert appt.status == "completed"  # unchanged

        logout(client)
