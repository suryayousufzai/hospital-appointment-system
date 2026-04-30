"""
Patient routes — dashboard, profile, edit profile, appointment history.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.forms import EditPatientForm
from app.utils.decorators import admin_required, patient_required

patient_bp = Blueprint("patient", __name__)


@patient_bp.route("/dashboard")
@login_required
@patient_required
def dashboard():
    """Patient's personal dashboard — upcoming & past appointments."""
    from datetime import date
    patient = current_user.patient_profile
    today   = date.today()

    upcoming = (
        Appointment.query
        .filter(Appointment.patient_id == patient.id,
                Appointment.appointment_date >= today,
                Appointment.status.in_(["pending", "confirmed"]))
        .order_by(Appointment.appointment_date, Appointment.appointment_time)
        .all()
    )
    history = (
        Appointment.query
        .filter(Appointment.patient_id == patient.id,
                Appointment.appointment_date < today)
        .order_by(Appointment.appointment_date.desc())
        .limit(10).all()
    )
    stats = {
        "total":     Appointment.query.filter_by(patient_id=patient.id).count(),
        "upcoming":  len(upcoming),
        "completed": Appointment.query.filter_by(patient_id=patient.id,
                                                  status="completed").count(),
        "cancelled": Appointment.query.filter_by(patient_id=patient.id,
                                                  status="cancelled").count(),
    }
    return render_template("patient/dashboard.html",
                           patient=patient, upcoming=upcoming,
                           history=history, stats=stats)


@patient_bp.route("/")
@login_required
@admin_required
def list_patients():
    """Admin only — list all patients with optional search."""
    q = request.args.get("q", "").strip()
    from app.models.user import User
    query = Patient.query.join(Patient.user)
    if q:
        like = f"%{q}%"
        query = query.filter(
            User.first_name.ilike(like) |
            User.last_name.ilike(like)  |
            User.email.ilike(like)
        )
    patients = query.order_by(Patient.id.desc()).all()
    return render_template("patient/list.html", patients=patients, q=q)


@patient_bp.route("/<int:patient_id>")
@login_required
def view_patient(patient_id):
    """View a patient profile — admin / doctor see all, patient sees own."""
    patient = Patient.query.get_or_404(patient_id)

    if not (current_user.is_admin() or current_user.is_doctor() or
            (current_user.is_patient() and
             current_user.patient_profile.id == patient_id)):
        flash("Access denied.", "danger")
        return redirect(url_for("auth.index"))

    appointments = (
        Appointment.query
        .filter_by(patient_id=patient.id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )
    return render_template("patient/profile.html",
                           patient=patient, appointments=appointments)


@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Edit patient profile — patient edits own, admin edits any."""
    patient = Patient.query.get_or_404(patient_id)

    if not (current_user.is_admin() or
            (current_user.is_patient() and
             current_user.patient_profile.id == patient_id)):
        flash("Access denied.", "danger")
        return redirect(url_for("auth.index"))

    form = EditPatientForm()
    if form.validate_on_submit():
        patient.user.first_name     = form.first_name.data.strip()
        patient.user.last_name      = form.last_name.data.strip()
        patient.date_of_birth       = form.date_of_birth.data
        patient.gender              = form.gender.data
        patient.blood_type          = form.blood_type.data
        patient.phone               = form.phone.data
        patient.address             = form.address.data
        patient.emergency_contact   = form.emergency_contact.data
        patient.medical_history     = form.medical_history.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("patient.view_patient", patient_id=patient.id))

    # Pre-fill form
    form.first_name.data        = patient.user.first_name
    form.last_name.data         = patient.user.last_name
    form.date_of_birth.data     = patient.date_of_birth
    form.gender.data            = patient.gender
    form.blood_type.data        = patient.blood_type
    form.phone.data             = patient.phone
    form.address.data           = patient.address
    form.emergency_contact.data = patient.emergency_contact
    form.medical_history.data   = patient.medical_history

    return render_template("patient/edit.html", form=form, patient=patient)
