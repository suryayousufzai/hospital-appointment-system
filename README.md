# 🏥 Hospital Appointment Management System

A full-featured web application built with **Flask** that allows patients, doctors, and administrators to manage hospital appointments efficiently.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Team Members](#team-members)

---

## ✨ Features

### 👤 Authentication & Authorization
- Secure login and registration system
- Role-based access control: **Admin**, **Doctor**, **Patient**
- Password hashing with Bcrypt
- Session management with Flask-Login

### 🩺 Doctor Management
- Add, edit, and deactivate doctor profiles
- Assign doctors to departments
- Manage availability schedules (days and hours)
- Search doctors by name, specialty, or department

### 🧑‍⚕️ Patient Management
- Patient self-registration
- Admin can view and manage all patient accounts
- Store medical history, blood type, emergency contacts

### 📅 Appointment System
- Patients can book appointments with available doctors
- Real-time availability checking
- Appointment statuses: `pending → confirmed → completed / cancelled`
- View full appointment history (patient and doctor views)
- Doctors can add notes after a visit

### 🏢 Department Management
- Admin can create and manage hospital departments
- Doctors are assigned to departments

---

## 🛠 Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Backend     | Python 3.11+, Flask 3.0             |
| Database    | SQLite via Flask-SQLAlchemy         |
| Auth        | Flask-Login, Flask-Bcrypt           |
| Forms       | Flask-WTF, WTForms                  |
| Frontend    | HTML5, CSS3, Bootstrap 5, JavaScript |
| Testing     | Pytest, pytest-flask                |

---

## 📁 Project Structure

```
hospital_system/
│
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   ├── routes/              # Blueprint route handlers
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/
│       └── decorators.py    # RBAC decorators
│
├── tests/                   # Unit and integration tests
├── config.py                # App configuration
├── run.py                   # Entry point
└── requirements.txt
```

---

## 🗃 Database Schema

```
users
  id, username, email, password_hash, role, first_name, last_name, is_active, created_at

departments
  id, name, description

doctors
  id, user_id (FK→users), department_id (FK→departments),
  specialty, phone, bio, available_days, available_from,
  available_to, consultation_fee, is_available, created_at

patients
  id, user_id (FK→users), date_of_birth, gender, blood_type,
  phone, address, emergency_contact, medical_history, created_at

appointments
  id, patient_id (FK→patients), doctor_id (FK→doctors),
  appointment_date, appointment_time, status, reason, notes,
  created_at, updated_at
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint       | Description              | Access  |
|--------|----------------|--------------------------|---------|
| GET    | `/`            | Landing / redirect       | Public  |
| GET    | `/login`       | Login page               | Public  |
| POST   | `/login`       | Authenticate user        | Public  |
| GET    | `/register`    | Registration page        | Public  |
| POST   | `/register`    | Create patient account   | Public  |
| GET    | `/logout`      | Log out current user     | Auth    |

### Admin
| Method | Endpoint              | Description              | Access |
|--------|-----------------------|--------------------------|--------|
| GET    | `/admin/dashboard`    | Admin overview           | Admin  |
| GET    | `/admin/users`        | Manage all users         | Admin  |
| GET    | `/admin/departments`  | Manage departments       | Admin  |

### Doctors
| Method | Endpoint                  | Description           | Access      |
|--------|---------------------------|-----------------------|-------------|
| GET    | `/doctors/`               | List all doctors      | Auth        |
| GET    | `/doctors/<id>`           | Doctor profile        | Auth        |
| GET    | `/doctors/dashboard`      | Doctor's dashboard    | Doctor      |

### Patients
| Method | Endpoint                  | Description           | Access      |
|--------|---------------------------|-----------------------|-------------|
| GET    | `/patients/`              | List all patients     | Admin       |
| GET    | `/patients/<id>`          | Patient profile       | Auth        |
| GET    | `/patients/dashboard`     | Patient dashboard     | Patient     |

### Appointments
| Method | Endpoint                      | Description              | Access  |
|--------|-------------------------------|--------------------------|---------|
| GET    | `/appointments/`              | List appointments        | Auth    |
| GET    | `/appointments/book`          | Booking form             | Patient |
| POST   | `/appointments/book`          | Submit booking           | Patient |
| GET    | `/appointments/<id>`          | Appointment detail       | Auth    |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or newer
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hospital-appointment-system.git
cd hospital-appointment-system
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

Visit **http://127.0.0.1:5000** in your browser.

### 5. Default Admin Account

```
Email    : admin@hospital.com
Password : Admin@1234
```

> ⚠️ Change the admin password after your first login.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_auth.py
```

---

## 👥 Team Members

| Name | Role |
|------|------|
| Member 1 | Auth & User Management |
| Member 2 | Doctor & Department Module |
| Member 3 | Patient Module |
| Member 4 | Appointment Module |
| Member 5 | UI/UX & Testing |

---

## 📄 License

This project was created for academic purposes as part of a Flask web development course.
