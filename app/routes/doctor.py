"""
Doctor routes — list, profile, dashboard, edit.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.doctor import Doctor, Department
from app.models.appointment import Appointment
from app.forms import EditDoctorForm
from app.utils.decorators import admin_required, admin_or_doctor_required

doctor_bp = Blueprint("doctor", __name__)


@doctor_bp.route("/dashboard")
@login_required
def dashboard():
    """Doctor's personal dashboard — own appointments."""
    if not current_user.is_doctor():
        return redirect(url_for("auth.index"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    pending = Appointment.query.filter_by(
        doctor_id=doctor.id, status="pending"
    ).order_by(Appointment.appointment_date).all()
    confirmed = Appointment.query.filter_by(
        doctor_id=doctor.id, status="confirmed"
    ).order_by(Appointment.appointment_date).all()
    history = Appointment.query.filter_by(
        doctor_id=doctor.id
    ).filter(
        Appointment.status.in_(["completed", "cancelled"])
    ).order_by(Appointment.appointment_date.desc()).limit(10).all()

    return render_template(
        "doctor/dashboard.html",
        doctor=doctor,
        pending=pending,
        confirmed=confirmed,
        history=history,
    )


@doctor_bp.route("/")
@login_required
def list_doctors():
    """Browse all doctors with search by name, specialty, or department."""
    q = request.args.get("q", "").strip()
    dept_id = request.args.get("dept", type=int)

    query = Doctor.query.join(Doctor.user)
    if q:
        from app.models.user import User
        query = query.filter(
            Doctor.specialty.ilike(f"%{q}%") |
            User.first_name.ilike(f"%{q}%") |
            User.last_name.ilike(f"%{q}%")
        )
    if dept_id:
        query = query.filter(Doctor.department_id == dept_id)

    doctors = query.filter(Doctor.is_available == True).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        "doctor/list.html",
        doctors=doctors,
        departments=departments,
        q=q,
        dept_id=dept_id,
    )


@doctor_bp.route("/<int:doctor_id>")
@login_required
def view_doctor(doctor_id):
    """View a single doctor's public profile."""
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("doctor/profile.html", doctor=doctor)


@doctor_bp.route("/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_doctor_required
def edit_doctor(doctor_id):
    """Edit a doctor profile (admin or the doctor themselves)."""
    doctor = Doctor.query.get_or_404(doctor_id)

    # Doctors can only edit their own profile
    if current_user.is_doctor() and doctor.user_id != current_user.id:
        flash("You can only edit your own profile.", "danger")
        return redirect(url_for("doctor.view_doctor", doctor_id=doctor_id))

    form = EditDoctorForm()
    form.department_id.choices = [
        (d.id, d.name) for d in Department.query.order_by(Department.name).all()
    ]
    # Pre-fill user fields
    if request.method == "GET":
        form.first_name.data = doctor.user.first_name
        form.last_name.data = doctor.user.last_name
        form.username.data = doctor.user.username
        form.email.data = doctor.user.email
        form.available_days.data = doctor.available_days_list

    if form.validate_on_submit():
        doctor.user.first_name = form.first_name.data.strip()
        doctor.user.last_name = form.last_name.data.strip()
        doctor.department_id = form.department_id.data
        doctor.specialty = form.specialty.data.strip()
        doctor.phone = form.phone.data
        doctor.bio = form.bio.data
        doctor.consultation_fee = form.consultation_fee.data or 0.0
        doctor.available_days = ",".join(form.available_days.data)
        doctor.available_from = form.available_from.data
        doctor.available_to = form.available_to.data
        doctor.is_available = form.is_available.data


        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("doctor.view_doctor", doctor_id=doctor.id))

    return render_template("doctor/edit.html", form=form, doctor=doctor)


@doctor_bp.route("/<int:doctor_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_doctor(doctor_id):
    """Admin: toggle doctor availability."""
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_available = not doctor.is_available
    db.session.commit()
    status = "available" if doctor.is_available else "unavailable"
    flash(f"Dr. {doctor.user.full_name} marked as {status}.", "success")
    return redirect(url_for("doctor.list_doctors"))
