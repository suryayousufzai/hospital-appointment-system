"""
Authentication routes — Login, Register, Logout.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.models.patient import Patient
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Landing page — redirect authenticated users to their dashboard."""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("admin.dashboard"))
        elif current_user.is_doctor():
            return redirect(url_for("doctor.dashboard"))
        else:
            return redirect(url_for("patient.dashboard"))
    return render_template("auth/landing.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login with email and password."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Contact an administrator.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.first_name}!", "success")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("auth.index"))

        flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle new patient self-registration."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role="patient",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        patient = Patient(user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
