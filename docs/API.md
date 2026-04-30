# 🏥 Hospital Appointment Management System — API Documentation

## Overview

This document describes all HTTP routes exposed by the application.
The system uses session-based authentication (cookies) via Flask-Login.

---

## Authentication

All routes except **Public** require the user to be logged in.  
Role abbreviations used below:

| Symbol | Role |
|--------|------|
| 🌐 | Public (no login required) |
| 🔐 | Any authenticated user |
| 👑 | Admin only |
| 🩺 | Doctor only |
| 🧑 | Patient only |
| 👑🩺 | Admin or Doctor |

---

## Auth Routes

Base URL: `/`

| Method | Endpoint | Description | Access | Redirect |
|--------|----------|-------------|--------|----------|
| `GET` | `/` | Landing page / role-based redirect | 🌐 | Dashboard if logged in |
| `GET` | `/login` | Render login form | 🌐 | Dashboard if logged in |
| `POST` | `/login` | Authenticate user | 🌐 | Dashboard on success |
| `GET` | `/register` | Render registration form | 🌐 | Dashboard if logged in |
| `POST` | `/register` | Create new patient account | 🌐 | `/login` on success |
| `GET` | `/logout` | Log out current user | 🔐 | `/login` |

### POST `/login` — Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Registered email address |
| `password` | string | ✅ | Account password |
| `remember` | boolean | ❌ | Keep session alive |

### POST `/register` — Request Body

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `first_name` | string | ✅ | 2–64 characters |
| `last_name` | string | ✅ | 2–64 characters |
| `username` | string | ✅ | 3–64 chars, unique |
| `email` | string | ✅ | Valid email, unique |
| `password` | string | ✅ | Min 8 characters |
| `confirm_password` | string | ✅ | Must match password |

---

## Admin Routes

Base URL: `/admin`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/admin/dashboard` | Admin overview with statistics | 👑 |
| `GET` | `/admin/users` | List all users (search: `?q=`) | 👑 |
| `GET` | `/admin/users/<id>/edit` | Edit user form | 👑 |
| `POST` | `/admin/users/<id>/edit` | Save user changes | 👑 |
| `POST` | `/admin/users/<id>/toggle` | Activate / deactivate account | 👑 |
| `GET` | `/admin/doctors/add` | Add new doctor form | 👑 |
| `POST` | `/admin/doctors/add` | Create doctor account + profile | 👑 |
| `GET` | `/admin/departments` | List departments + add form | 👑 |
| `POST` | `/admin/departments/add` | Create new department | 👑 |
| `POST` | `/admin/departments/<id>/delete` | Delete empty department | 👑 |

### POST `/admin/doctors/add` — Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | ✅ | Doctor first name |
| `last_name` | string | ✅ | Doctor last name |
| `username` | string | ✅ | Unique login username |
| `email` | string | ✅ | Unique email address |
| `password` | string | ✅ | Initial password (min 8 chars) |
| `specialty` | string | ✅ | Medical specialty |
| `department_id` | integer | ✅ | FK → departments.id |
| `phone` | string | ❌ | Contact number |
| `bio` | string | ❌ | Professional biography (max 500) |
| `available_days` | string | ❌ | Comma-separated days |
| `available_from` | string | ❌ | Start time `HH:MM` |
| `available_to` | string | ❌ | End time `HH:MM` |
| `consultation_fee` | float | ❌ | Fee in USD |

---

## Doctor Routes

Base URL: `/doctors`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/doctors/dashboard` | Doctor's personal dashboard | 🩺 |
| `GET` | `/doctors/` | List all doctors (search: `?q=`, filter: `?dept=`) | 🔐 |
| `GET` | `/doctors/<id>` | View doctor profile | 🔐 |
| `GET` | `/doctors/<id>/edit` | Edit doctor form | 👑🩺 (own only for doctor) |
| `POST` | `/doctors/<id>/edit` | Save doctor profile changes | 👑🩺 |

### POST `/doctors/<id>/edit` — Request Body

| Field | Type | Required |
|-------|------|----------|
| `first_name` | string | ✅ |
| `last_name` | string | ✅ |
| `specialty` | string | ✅ |
| `department_id` | integer | ✅ |
| `phone` | string | ❌ |
| `bio` | string | ❌ |
| `available_days` | string | ❌ |
| `available_from` | string | ❌ |
| `available_to` | string | ❌ |
| `consultation_fee` | float | ❌ |
| `is_available` | boolean | ❌ |

---

## Patient Routes

Base URL: `/patients`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/patients/dashboard` | Patient's personal dashboard | 🧑 |
| `GET` | `/patients/` | List all patients (search: `?q=`) | 👑 |
| `GET` | `/patients/<id>` | View patient profile | 👑🩺 or own |
| `GET` | `/patients/<id>/edit` | Edit patient profile form | 👑 or own |
| `POST` | `/patients/<id>/edit` | Save patient profile changes | 👑 or own |

### POST `/patients/<id>/edit` — Request Body

| Field | Type | Required |
|-------|------|----------|
| `first_name` | string | ✅ |
| `last_name` | string | ✅ |
| `date_of_birth` | date `YYYY-MM-DD` | ❌ |
| `gender` | string | ❌ | `Male`, `Female`, `Other` |
| `blood_type` | string | ❌ | `A+`, `A-`, `B+` … |
| `phone` | string | ❌ |
| `address` | string | ❌ |
| `emergency_contact` | string | ❌ |
| `medical_history` | string | ❌ | max 1000 chars |

---

## Appointment Routes

Base URL: `/appointments`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/appointments/` | List appointments (filter: `?status=`) | 🔐 (role-filtered) |
| `GET` | `/appointments/book` | Booking form | 🧑 |
| `POST` | `/appointments/book` | Submit new booking | 🧑 |
| `GET` | `/appointments/<id>` | View appointment details | 🔐 (own only) |
| `POST` | `/appointments/<id>/update` | Update status + notes | 👑🩺 |
| `POST` | `/appointments/<id>/cancel` | Cancel appointment | 🔐 (own only) |

### POST `/appointments/book` — Request Body

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `doctor_id` | integer | ✅ | Must be available doctor |
| `appointment_date` | date `YYYY-MM-DD` | ✅ | Cannot be in the past |
| `appointment_time` | string | ✅ | One of the fixed slots |
| `reason` | string | ❌ | Max 500 chars |

**Business Rules:**
- Cannot book a date in the past
- Cannot double-book the same doctor/date/time slot
- Doctor must have `is_available = True`

### POST `/appointments/<id>/update` — Request Body

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `status` | string | ✅ | `pending`, `confirmed`, `completed`, `cancelled` |
| `notes` | string | ❌ | Doctor's clinical notes (max 1000 chars) |

### Appointment Status Flow

```
pending ──► confirmed ──► completed
    │              │
    └──────────────┴──► cancelled
```

---

## Data Models

### User

```
id            INTEGER  PK
username      TEXT     UNIQUE NOT NULL
email         TEXT     UNIQUE NOT NULL
password_hash TEXT     NOT NULL
role          TEXT     NOT NULL  -- 'admin' | 'doctor' | 'patient'
first_name    TEXT     NOT NULL
last_name     TEXT     NOT NULL
is_active     BOOLEAN  DEFAULT TRUE
created_at    DATETIME DEFAULT NOW
```

### Department

```
id          INTEGER  PK
name        TEXT     UNIQUE NOT NULL
description TEXT
```

### Doctor

```
id               INTEGER  PK
user_id          INTEGER  FK → users.id  UNIQUE
department_id    INTEGER  FK → departments.id
specialty        TEXT     NOT NULL
phone            TEXT
bio              TEXT
available_days   TEXT     -- e.g. "Monday,Wednesday,Friday"
available_from   TEXT     -- HH:MM
available_to     TEXT     -- HH:MM
consultation_fee REAL     DEFAULT 0
is_available     BOOLEAN  DEFAULT TRUE
created_at       DATETIME DEFAULT NOW
```

### Patient

```
id                INTEGER  PK
user_id           INTEGER  FK → users.id  UNIQUE
date_of_birth     DATE
gender            TEXT
blood_type        TEXT
phone             TEXT
address           TEXT
emergency_contact TEXT
medical_history   TEXT
created_at        DATETIME DEFAULT NOW
```

### Appointment

```
id               INTEGER  PK
patient_id       INTEGER  FK → patients.id
doctor_id        INTEGER  FK → doctors.id
appointment_date DATE     NOT NULL
appointment_time TEXT     NOT NULL  -- HH:MM
status           TEXT     DEFAULT 'pending'
reason           TEXT
notes            TEXT
created_at       DATETIME DEFAULT NOW
updated_at       DATETIME DEFAULT NOW
```

---

## Error Responses

| Code | Page | Description |
|------|------|-------------|
| `302` | Redirect | Unauthenticated access — redirected to `/login` |
| `403` | `403.html` | Authenticated but insufficient role permissions |
| `404` | `404.html` | Resource not found |
| `500` | `500.html` | Internal server error |

---

## CSRF Protection

All `POST` forms include a CSRF token via Flask-WTF.  
Every form must include `{{ form.hidden_tag() }}` or a manual `csrf_token` field.  
CSRF is automatically disabled in the test environment (`WTF_CSRF_ENABLED = False`).
