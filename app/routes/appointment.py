"""
Appointment routes — list, book, view detail, update status, cancel.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import date

from app import db
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.forms import BookAppointmentForm, UpdateAppointmentForm

appointment_bp = Blueprint("appointment", __name__)


@appointment_bp.route("/")
@login_required
def list_appointments():
    """
    List appointments filtered by role:
    - Admin  → all appointments
    - Doctor → their own appointments
    - Patient→ their own appointments
    """
    status_filter = request.args.get("status", "")
    query = Appointment.query

    if current_user.is_doctor():
        query = query.filter_by(doctor_id=current_user.doctor_profile.id)
    elif current_user.is_patient():
        query = query.filter_by(patient_id=current_user.patient_profile.id)

    if status_filter and status_filter in Appointment.ALL_STATUSES:
        query = query.filter_by(status=status_filter)

    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()

    return render_template("appointment/list.html",
                           appointments=appointments,
                           status_filter=status_filter,
                           ALL_STATUSES=Appointment.ALL_STATUSES)


@appointment_bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    """Patient books a new appointment."""
    if not (current_user.is_patient() or current_user.is_admin()):
        flash("Only patients can book appointments.", "warning")
        return redirect(url_for("appointment.list_appointments"))

    form = BookAppointmentForm()
    available_doctors = Doctor.query.filter_by(is_available=True).all()
    form.doctor_id.choices = [
        (d.id, f"Dr. {d.user.full_name} — {d.specialty} (${d.consultation_fee:.0f})")
        for d in available_doctors
    ]

    if form.validate_on_submit():
        if not current_user.is_patient():
            flash("Admin cannot book appointments directly.", "warning")
            return redirect(url_for("appointment.list_appointments"))

        patient_id = current_user.patient_profile.id

        # Reject past dates
        if form.appointment_date.data < date.today():
            flash("Cannot book an appointment in the past.", "warning")
            return render_template("appointment/book.html",
                                   form=form, available_doctors=available_doctors)

        # Check for duplicate slot
        existing = Appointment.query.filter_by(
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
        ).filter(Appointment.status.in_(["pending", "confirmed"])).first()

        if existing:
            flash("That time slot is already booked. Please choose another.", "warning")
        else:
            appt = Appointment(
                patient_id=patient_id,
                doctor_id=form.doctor_id.data,
                appointment_date=form.appointment_date.data,
                appointment_time=form.appointment_time.data,
                reason=form.reason.data,
                status="pending",
            )
            db.session.add(appt)
            db.session.commit()
            flash("Appointment booked successfully! Status: Pending.", "success")
            return redirect(url_for("appointment.view_appointment",
                                    appointment_id=appt.id))

    return render_template("appointment/book.html",
                           form=form, available_doctors=available_doctors)


@appointment_bp.route("/<int:appointment_id>")
@login_required
def view_appointment(appointment_id):
    """View a single appointment's full details."""
    appt = Appointment.query.get_or_404(appointment_id)
    _check_access(appt)

    form = UpdateAppointmentForm()
    form.status.data = appt.status
    form.notes.data  = appt.notes
    return render_template("appointment/detail.html", appt=appt, form=form)


@appointment_bp.route("/<int:appointment_id>/update", methods=["POST"])
@login_required
def update_appointment(appointment_id):
    """Admin or doctor updates status and/or adds notes."""
    appt = Appointment.query.get_or_404(appointment_id)

    if not (current_user.is_admin() or current_user.is_doctor()):
        flash("Access denied.", "danger")
        return redirect(url_for("appointment.view_appointment",
                                appointment_id=appointment_id))

    form = UpdateAppointmentForm()
    if form.validate_on_submit():
        appt.status = form.status.data
        appt.notes  = form.notes.data
        db.session.commit()
        flash("Appointment updated successfully.", "success")
    else:
        flash("Invalid form submission.", "danger")

    return redirect(url_for("appointment.view_appointment",
                            appointment_id=appointment_id))


@appointment_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    """Patient, doctor, or admin cancels an appointment."""
    appt = Appointment.query.get_or_404(appointment_id)
    _check_access(appt)

    if appt.status in ["completed", "cancelled"]:
        flash("This appointment cannot be cancelled.", "warning")
    else:
        appt.status = "cancelled"
        db.session.commit()
        flash("Appointment cancelled.", "info")

    return redirect(url_for("appointment.list_appointments"))


def _check_access(appt):
    """Abort 403 if the current user has no right to see this appointment."""
    if current_user.is_admin():
        return
    if current_user.is_doctor() and current_user.doctor_profile.id == appt.doctor_id:
        return
    if current_user.is_patient() and current_user.patient_profile.id == appt.patient_id:
        return
    abort(403)
