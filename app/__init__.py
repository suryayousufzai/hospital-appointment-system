"""
Application factory for the Hospital Appointment Management System.
Uses the Flask app factory pattern for flexibility and testability.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

from config import config

# Initialize extensions (not yet bound to an app)
db           = SQLAlchemy()
login_manager = LoginManager()
bcrypt       = Bcrypt()
csrf         = CSRFProtect()

# Configure login manager
login_manager.login_view         = "auth.login"
login_manager.login_message      = "Please log in to access this page."
login_manager.login_message_category = "warning"


def create_app(config_name="default"):
    """
    Application factory function.

    Args:
        config_name (str): One of 'development', 'testing', 'production', or 'default'.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Bind extensions to app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)           # makes csrf_token() available in all templates

    # Register blueprints
    from app.routes.auth        import auth_bp
    from app.routes.admin       import admin_bp
    from app.routes.doctor      import doctor_bp
    from app.routes.patient     import patient_bp
    from app.routes.appointment import appointment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,        url_prefix="/admin")
    app.register_blueprint(doctor_bp,       url_prefix="/doctors")
    app.register_blueprint(patient_bp,      url_prefix="/patients")
    app.register_blueprint(appointment_bp,  url_prefix="/appointments")

    # ── Error handlers ────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("500.html"), 500

    # ── Template context processors ───────────────────────────
    @app.context_processor
    def inject_globals():
        """Make useful variables available in every template."""
        from datetime import date
        return dict(current_date=date.today())

    # Create all database tables on first run
    with app.app_context():
        from app.models import user, doctor, patient, appointment  # noqa: F401
        db.create_all()
        _seed_default_admin()

    return app


def _seed_default_admin():
    """Create a default admin user if none exists."""
    from app.models.user import User

    if not User.query.filter_by(role="admin").first():
        admin = User(
            username="admin",
            email="admin@hospital.com",
            role="admin",
            first_name="System",
            last_name="Administrator",
        )
        admin.set_password("Admin@1234")
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created → email: admin@hospital.com | password: Admin@1234")
