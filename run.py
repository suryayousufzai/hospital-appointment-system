"""
Entry point for the Hospital Appointment Management System.

Run with:
    python run.py

Or with Flask CLI:
    flask run
"""

import os
from app import create_app

# Pick config based on environment variable, default to development
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    print("🏥 Starting Hospital Appointment Management System...")
    print(f"   Environment : {config_name}")
    print(f"   Debug Mode  : {app.config['DEBUG']}")
    print(f"   URL         : http://127.0.0.1:5000\n")
    app.run(debug=app.config["DEBUG"])
