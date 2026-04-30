"""
Admin routes — dashboard, users, departments, doctor creation.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from datetime import date

from app import db
from app.models.user import User
from app.models.doctor import Doctor, Department
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.forms import AddDoctorForm, EditUserForm, DepartmentForm
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Admin overview with key stats and recent appointments."""
    stats = {
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "departments": Department.query.count(),
        "today_appointments": Appointment.query.filter_by(
            appointment_date=date.today()
        ).count(),
    }
    recent_appointments = (
        Appointment.query
        .order_by(Appointment.created_at.desc())
        .limit(8)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_appointments=recent_appointments
    )


# ── Users ────────────────────────────────────────────────────
@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    """List all users with search and filter."""
    q = request.args.get("q", "").strip()
    role = request.args.get("role", "")
    query = User.query
    if q:
        query = query.filter(
            (User.first_name.ilike(f"%{q}%")) |
            (User.last_name.ilike(f"%{q}%")) |
            (User.email.ilike(f"%{q}%"))
        )
    if role:
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, q=q, role=role)


@admin_bp.route("/users/<int:user_id>/toggle")
@login_required
@admin_required
def toggle_user(user_id):
    """Activate or deactivate a user account."""
    user = User.query.get_or_404(user_id)
    if user.id == 1:
        flash("Cannot deactivate the primary admin.", "warning")
        return redirect(url_for("admin.manage_users"))
    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.full_name} has been {status}.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    """Permanently delete a user and their associated profile."""
    user = User.query.get_or_404(user_id)
    if user.id == 1:
        flash("Cannot delete the primary admin.", "danger")
        return redirect(url_for("admin.manage_users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.full_name} has been deleted.", "success")
    return redirect(url_for("admin.manage_users"))


# ── Departments ──────────────────────────────────────────────
@admin_bp.route("/departments")
@login_required
@admin_required
def manage_departments():
    """List all departments."""
    departments = Department.query.order_by(Department.name).all()
    form = DepartmentForm()
    return render_template("admin/departments.html", departments=departments, form=form)


@admin_bp.route("/departments/add", methods=["POST"])
@login_required
@admin_required
def add_department():
    """Add a new department."""
    form = DepartmentForm()
    if form.validate_on_submit():
        if Department.query.filter_by(name=form.name.data.strip()).first():
            flash("A department with that name already exists.", "warning")
        else:
            dept = Department(
                name=form.name.data.strip(),
                description=form.description.data
            )
            db.session.add(dept)
            db.session.commit()
            flash(f"Department '{dept.name}' created.", "success")
    else:
        flash("Please correct the form errors.", "danger")
    return redirect(url_for("admin.manage_departments"))


@admin_bp.route("/departments/<int:dept_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_department(dept_id):
    """Delete a department (only if no doctors assigned)."""
    dept = Department.query.get_or_404(dept_id)
    if dept.doctors:
        flash("Cannot delete a department that has doctors assigned.", "warning")
    else:
        db.session.delete(dept)
        db.session.commit()
        flash(f"Department '{dept.name}' deleted.", "success")
    return redirect(url_for("admin.manage_departments"))


# ── Doctors (admin creation) ─────────────────────────────────
@admin_bp.route("/doctors/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_doctor():
    """Create a new doctor account and profile."""
    form = AddDoctorForm()
    form.department_id.choices = [
        (d.id, d.name) for d in Department.query.order_by(Department.name).all()
    ]
    if form.validate_on_submit():
        # Check uniqueness
        if User.query.filter_by(email=form.email.data.strip().lower()).first():
            flash("Email already registered.", "danger")
            return render_template("admin/add_doctor.html", form=form)
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("Username already taken.", "danger")
            return render_template("admin/add_doctor.html", form=form)

        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role="doctor",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        doctor = Doctor(
            user_id=user.id,
            department_id=form.department_id.data,
            specialty=form.specialty.data.strip(),
            phone=form.phone.data,
            bio=form.bio.data,
            consultation_fee=form.consultation_fee.data or 0.0,
            available_days=form.available_days.data,
            available_from=form.available_from.data,
            available_to=form.available_to.data,
        )
        db.session.add(doctor)
        db.session.commit()
        flash(f"Dr. {user.full_name} added successfully.", "success")
        return redirect(url_for("doctor.list_doctors"))

    return render_template("admin/add_doctor.html", form=form)
