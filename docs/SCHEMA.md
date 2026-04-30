# 🗃 Database Schema — Hospital Appointment Management System

## Entity Relationship Diagram

```
┌─────────────────────────────┐
│            users            │
├─────────────────────────────┤
│ id           INTEGER  PK    │
│ username     TEXT  UNIQUE   │
│ email        TEXT  UNIQUE   │
│ password_hash TEXT          │
│ role         TEXT           │◄── 'admin' | 'doctor' | 'patient'
│ first_name   TEXT           │
│ last_name    TEXT           │
│ is_active    BOOLEAN        │
│ created_at   DATETIME       │
└──────────────┬──────────────┘
               │ 1
       ┌───────┴────────┐
       │                │
       ▼ 1              ▼ 1
┌──────────────┐  ┌──────────────────┐
│   doctors    │  │     patients     │
├──────────────┤  ├──────────────────┤
│ id      PK   │  │ id          PK   │
│ user_id FK───┘  │ user_id  FK──────┘
│ dept_id FK   │  │ date_of_birth    │
│ specialty    │  │ gender           │
│ phone        │  │ blood_type       │
│ bio          │  │ phone            │
│ avail_days   │  │ address          │
│ avail_from   │  │ emergency_contact│
│ avail_to     │  │ medical_history  │
│ fee          │  │ created_at       │
│ is_available │  └────────┬─────────┘
│ created_at   │           │
└──────┬───────┘           │
       │ 1                 │ 1
       │    ┌──────────────┘
       │    │
       ▼ N  ▼ N
┌─────────────────────────────┐
│         appointments        │
├─────────────────────────────┤
│ id               INTEGER PK │
│ patient_id       FK → patients.id │
│ doctor_id        FK → doctors.id  │
│ appointment_date DATE        │
│ appointment_time TEXT        │
│ status           TEXT        │◄── pending|confirmed|completed|cancelled
│ reason           TEXT        │
│ notes            TEXT        │
│ created_at       DATETIME    │
│ updated_at       DATETIME    │
└─────────────────────────────┘

┌─────────────────────────────┐
│         departments         │◄── referenced by doctors.department_id
├─────────────────────────────┤
│ id          INTEGER  PK     │
│ name        TEXT  UNIQUE    │
│ description TEXT            │
└─────────────────────────────┘
```

## Table Details

### Normalization

The schema is in **Third Normal Form (3NF)**:

- **1NF** — All columns are atomic. No repeating groups.
- **2NF** — All non-key attributes depend fully on the primary key.
- **3NF** — No transitive dependencies (e.g., doctor specialty doesn't depend on department).

### Key Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| User → Doctor | One-to-One | A user with role `doctor` has one doctor profile |
| User → Patient | One-to-One | A user with role `patient` has one patient profile |
| Department → Doctor | One-to-Many | A department has many doctors |
| Doctor → Appointment | One-to-Many | A doctor can have many appointments |
| Patient → Appointment | One-to-Many | A patient can have many appointments |

### Indexes

| Table | Column | Type |
|-------|--------|------|
| `users` | `username` | UNIQUE INDEX |
| `users` | `email` | UNIQUE INDEX |
| `doctors` | `user_id` | UNIQUE INDEX |
| `patients` | `user_id` | UNIQUE INDEX |
| `departments` | `name` | UNIQUE INDEX |

### Appointment Status Transitions

```
[pending] ──► [confirmed] ──► [completed]
    │               │
    └───────────────┴──────► [cancelled]
```

- **pending** → Default state when a patient books
- **confirmed** → Doctor/admin confirms the slot
- **completed** → Visit has taken place (doctor adds notes)
- **cancelled** → Cancelled by any party before completion
