# Contributing Guide — Hospital Appointment Management System

## Git Workflow

### Branch Strategy

```
main          ← production-ready code only
  └── dev     ← integration branch
        ├── feature/auth
        ├── feature/doctors
        ├── feature/patients
        └── feature/appointments
```

### Step-by-step

```bash
# 1. Always branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name

# 2. Make your changes with clear commits
git add .
git commit -m "feat(auth): add login form validation"

# 3. Push and open a Pull Request into dev
git push origin feature/your-feature-name
```

---

## Commit Message Format

We follow **Conventional Commits**:

```
<type>(<scope>): <short description>
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructure (no feature or bug) |
| `test` | Adding or fixing tests |
| `chore` | Build process, dependencies |

### Scopes

`auth` · `admin` · `doctor` · `patient` · `appointment` · `db` · `ui` · `tests` · `deps`

### Examples

```bash
git commit -m "feat(appointment): add duplicate slot validation"
git commit -m "fix(auth): redirect loop on login for active session"
git commit -m "docs(api): add appointment update endpoint description"
git commit -m "test(patient): add profile edit integration test"
git commit -m "style(ui): improve stat card hover animation"
git commit -m "refactor(models): add full_name property to User model"
git commit -m "chore(deps): upgrade Flask to 3.0.3"
```

---

## Team Module Ownership

| Module | Owner | Files |
|--------|-------|-------|
| Auth & User Management | Member 1 | `routes/auth.py`, `templates/auth/` |
| Doctor & Department | Member 2 | `routes/admin.py`, `routes/doctor.py`, `templates/doctor/` |
| Patient Module | Member 3 | `routes/patient.py`, `templates/patient/` |
| Appointment Module | Member 4 | `routes/appointment.py`, `templates/appointment/` |
| UI/UX & Testing | Member 5 | `static/`, `tests/` |

---

## Code Standards

- Follow **PEP 8** for all Python code
- All route functions must have a **docstring**
- All models must have docstrings on class and key properties
- Maximum line length: **100 characters**
- Use `flask8` or `pylint` before committing

```bash
# Check PEP 8 compliance
pip install pycodestyle
pycodestyle app/ --max-line-length=100
```
