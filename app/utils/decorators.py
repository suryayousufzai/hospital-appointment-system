"""
Custom decorators for role-based access control (RBAC).
Use these on route functions to restrict access by user role.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Restrict a route to admin users only.
    Redirects to home with an error message if the user is not an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Access denied: Admins only.", "danger")
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def doctor_required(f):
    """
    Restrict a route to doctor users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_doctor():
            flash("Access denied: Doctors only.", "danger")
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def patient_required(f):
    """
    Restrict a route to patient users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_patient():
            flash("Access denied: Patients only.", "danger")
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def admin_or_doctor_required(f):
    """
    Restrict a route to admin or doctor users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (
            current_user.is_admin() or current_user.is_doctor()
        ):
            flash("Access denied.", "danger")
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
