"""
WTForms form definitions for the Hospital Appointment Management System.
All forms use Flask-WTF for CSRF protection.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, SelectField,
    TextAreaField, DateField, FloatField, BooleanField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional,
    NumberRange, ValidationError
)
from app.models.user import User


# ── Auth Forms ────────────────────────────────────────────────

class LoginForm(FlaskForm):
    """User login form."""
    email    = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit   = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """New patient self-registration form."""
    first_name       = StringField("First Name",  validators=[DataRequired(), Length(2, 64)])
    last_name        = StringField("Last Name",   validators=[DataRequired(), Length(2, 64)])
    username         = StringField("Username",    validators=[DataRequired(), Length(3, 64)])
    email            = EmailField("Email",        validators=[DataRequired(), Email()])
    password         = PasswordField("Password",  validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField("Confirm",   validators=[DataRequired(), EqualTo("password")])
    submit           = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


# ── Admin — Add Doctor Form ───────────────────────────────────

class AddDoctorForm(FlaskForm):
    """Admin form to register a new doctor (creates User + Doctor profile)."""
    first_name       = StringField("First Name",     validators=[DataRequired(), Length(2, 64)])
    last_name        = StringField("Last Name",      validators=[DataRequired(), Length(2, 64)])
    username         = StringField("Username",       validators=[DataRequired(), Length(3, 64)])
    email            = EmailField("Email",           validators=[DataRequired(), Email()])
    password         = PasswordField("Password",     validators=[DataRequired(), Length(8, 128)])
    specialty        = StringField("Specialty",      validators=[DataRequired(), Length(2, 100)])
    department_id    = SelectField("Department",     coerce=int, validators=[DataRequired()])
    phone            = StringField("Phone",          validators=[Optional(), Length(max=20)])
    bio              = TextAreaField("Bio",           validators=[Optional(), Length(max=500)])
    available_days   = StringField("Available Days", validators=[Optional()])
    available_from   = StringField("From (HH:MM)",   validators=[Optional()])
    available_to     = StringField("To   (HH:MM)",   validators=[Optional()])
    consultation_fee = FloatField("Fee (USD)",       validators=[Optional(), NumberRange(min=0)])
    submit           = SubmitField("Add Doctor")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class EditDoctorForm(FlaskForm):
    """Edit an existing doctor's profile."""
    first_name       = StringField("First Name",     validators=[DataRequired(), Length(2, 64)])
    last_name        = StringField("Last Name",      validators=[DataRequired(), Length(2, 64)])
    specialty        = StringField("Specialty",      validators=[DataRequired(), Length(2, 100)])
    department_id    = SelectField("Department",     coerce=int, validators=[DataRequired()])
    phone            = StringField("Phone",          validators=[Optional(), Length(max=20)])
    bio              = TextAreaField("Bio",           validators=[Optional(), Length(max=500)])
    available_days   = StringField("Available Days", validators=[Optional()])
    available_from   = StringField("From (HH:MM)",   validators=[Optional()])
    available_to     = StringField("To   (HH:MM)",   validators=[Optional()])
    consultation_fee = FloatField("Fee (USD)",       validators=[Optional(), NumberRange(min=0)])
    is_available     = BooleanField("Currently Accepting Patients")
    submit           = SubmitField("Save Changes")


# ── Department Form ───────────────────────────────────────────

class DepartmentForm(FlaskForm):
    """Add or edit a hospital department."""
    name        = StringField("Department Name", validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField("Description",   validators=[Optional(), Length(max=300)])
    submit      = SubmitField("Save")


# ── Patient Forms ─────────────────────────────────────────────

class EditPatientForm(FlaskForm):
    """Patient (or admin) edits a patient profile."""
    first_name        = StringField("First Name",        validators=[DataRequired(), Length(2, 64)])
    last_name         = StringField("Last Name",         validators=[DataRequired(), Length(2, 64)])
    date_of_birth     = DateField("Date of Birth",       validators=[Optional()])
    gender            = SelectField("Gender",            choices=[("", "— Select —"),
                                                                   ("Male", "Male"),
                                                                   ("Female", "Female"),
                                                                   ("Other", "Other")],
                                    validators=[Optional()])
    blood_type        = SelectField("Blood Type",        choices=[("", "— Unknown —"),
                                                                   ("A+","A+"),("A-","A-"),
                                                                   ("B+","B+"),("B-","B-"),
                                                                   ("AB+","AB+"),("AB-","AB-"),
                                                                   ("O+","O+"),("O-","O-")],
                                    validators=[Optional()])
    phone             = StringField("Phone",             validators=[Optional(), Length(max=20)])
    address           = StringField("Address",           validators=[Optional(), Length(max=255)])
    emergency_contact = StringField("Emergency Contact", validators=[Optional(), Length(max=150)])
    medical_history   = TextAreaField("Medical History", validators=[Optional(), Length(max=1000)])
    submit            = SubmitField("Save Profile")


# ── Appointment Forms ─────────────────────────────────────────

class BookAppointmentForm(FlaskForm):
    """Patient books a new appointment."""
    doctor_id        = SelectField("Select Doctor", coerce=int, validators=[DataRequired()])
    appointment_date = DateField("Date",            validators=[DataRequired()])
    appointment_time = SelectField("Time Slot",     validators=[DataRequired()],
                                   choices=[
                                       ("09:00","9:00 AM"), ("09:30","9:30 AM"),
                                       ("10:00","10:00 AM"),("10:30","10:30 AM"),
                                       ("11:00","11:00 AM"),("11:30","11:30 AM"),
                                       ("12:00","12:00 PM"),("14:00","2:00 PM"),
                                       ("14:30","2:30 PM"), ("15:00","3:00 PM"),
                                       ("15:30","3:30 PM"), ("16:00","4:00 PM"),
                                       ("16:30","4:30 PM"),
                                   ])
    reason           = TextAreaField("Reason for Visit", validators=[Optional(), Length(max=500)])
    submit           = SubmitField("Book Appointment")


class UpdateAppointmentForm(FlaskForm):
    """Doctor or admin updates appointment status and adds notes."""
    status = SelectField("Status", choices=[
                ("pending",   "Pending"),
                ("confirmed", "Confirmed"),
                ("completed", "Completed"),
                ("cancelled", "Cancelled"),
             ], validators=[DataRequired()])
    notes  = TextAreaField("Doctor's Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Update")


# ── Admin — Edit User Form ────────────────────────────────────

class EditUserForm(FlaskForm):
    """Admin edits a user's basic info and active status."""
    first_name = StringField("First Name", validators=[DataRequired(), Length(2, 64)])
    last_name  = StringField("Last Name",  validators=[DataRequired(), Length(2, 64)])
    is_active  = BooleanField("Account Active")
    submit     = SubmitField("Save Changes")
