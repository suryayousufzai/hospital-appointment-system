"""
seed.py — Populate the database with realistic sample data.

Run with:
    python seed.py

WARNING: This will CLEAR all existing data before seeding.
"""

from app import create_app, db
from app.models.user import User
from app.models.doctor import Doctor, Department
from app.models.patient import Patient
from app.models.appointment import Appointment
from datetime import date, timedelta

app = create_app("development")


def clear_data():
    Appointment.query.delete()
    Patient.query.delete()
    Doctor.query.delete()
    Department.query.delete()
    User.query.delete()
    db.session.commit()
    print("🗑  Cleared existing data.")


def seed_departments():
    dept_data = [
        ("Cardiology",       "Heart and cardiovascular system specialists"),
        ("Neurology",        "Brain, spine and nervous system specialists"),
        ("Orthopedics",      "Bone, joint and musculoskeletal specialists"),
        ("Pediatrics",       "Healthcare for infants, children and adolescents"),
        ("Dermatology",      "Skin, hair and nail specialists"),
        ("General Medicine", "Primary care and general health consultations"),
    ]
    depts = []
    for name, desc in dept_data:
        d = Department(name=name, description=desc)
        db.session.add(d)
        depts.append(d)
    db.session.flush()
    print(f"✅ Created {len(depts)} departments")
    return depts


def seed_admin():
    admin = User(
        username="admin", email="admin@hospital.com",
        first_name="System", last_name="Administrator", role="admin",
    )
    admin.set_password("Admin@1234")
    db.session.add(admin)
    db.session.flush()
    print("✅ Created admin  →  admin@hospital.com / Admin@1234")


def seed_doctors(depts):
    """Create 5 doctors using the provided names and phone numbers."""
    doctors_data = [
        # username       first      last          specialty               dept  fee    days                           from    to      phone
        ("surya",       "Surya",   "Yousufzai",  "Cardiologist",         0,    200.0, "Monday,Wednesday,Friday",     "09:00","17:00", "+41762742297"),
        ("alia",        "Alia",    "Noori",       "Neurologist",          1,    220.0, "Tuesday,Thursday",            "08:00","16:00", "+93762742498"),
        ("faezah",      "Faezah",  "Ahmadi",      "Orthopedic Surgeon",   2,    180.0, "Monday,Tuesday,Thursday",     "10:00","18:00", "+93762572287"),
        ("lima",        "Lima",    "Wahedi",      "Pediatrician",         3,    150.0, "Monday,Wednesday,Friday",     "09:00","17:00", "+41782737267"),
        ("raufa",       "Raufa",   "Rauf",        "General Practitioner", 5,    120.0, "Monday,Tuesday,Wednesday,Thursday,Friday", "08:00","17:00", "+41762742297"),
    ]

    bios = {
        "Cardiologist":        "Board-certified cardiologist with 12+ years of experience in interventional cardiology.",
        "Neurologist":         "Specialist in neurological disorders including epilepsy, migraine, and stroke rehabilitation.",
        "Orthopedic Surgeon":  "Expertise in sports injuries, joint replacement, and minimally invasive procedures.",
        "Pediatrician":        "Dedicated to providing comprehensive healthcare for children from newborns through adolescence.",
        "General Practitioner":"Primary care physician focused on preventive medicine and chronic disease management.",
    }

    created = []
    for username, first, last, specialty, dept_idx, fee, days, frm, to, phone in doctors_data:
        u = User(
            username=f"dr.{username}",
            email=f"{username}@hospital.com",
            first_name=first, last_name=last, role="doctor"
        )
        u.set_password("Doctor@1234")
        db.session.add(u)
        db.session.flush()

        d = Doctor(
            user_id=u.id,
            department_id=depts[dept_idx].id,
            specialty=specialty,
            phone=phone,
            bio=bios.get(specialty, ""),
            consultation_fee=fee,
            available_days=days,
            available_from=frm,
            available_to=to,
        )
        db.session.add(d)
        created.append(d)

    db.session.flush()
    print(f"✅ Created {len(created)} doctors  →  password: Doctor@1234")
    return created


def seed_patients():
    """Create 5 patients using the provided names and phone numbers."""
    patients_data = [
        # username    first     last         dob           gender   blood  phone             address
        ("surya_p",  "Surya",  "Yousufzai", "1992-04-10", "Female","A+",  "+41762742297",   "12 Bahnhofstrasse, Zurich"),
        ("alia_p",   "Alia",   "Noori",      "1988-07-22", "Female","B-",  "+93762742498",   "34 Kabul Street, Lausanne"),
        ("faezah_p", "Faezah", "Ahmadi",     "1995-01-15", "Female","O+",  "+93762572287",   "56 Rue de Berne, Geneva"),
        ("lima_p",   "Lima",   "Wahedi",     "2001-09-03", "Female","AB+", "+41782737267",   "78 Avenue de la Gare, Bern"),
        ("raufa_p",  "Raufa",  "Rauf",       "1979-11-28", "Female","A-",  "+41762742297",   "90 Seestrasse, Basel"),
    ]

    medical_histories = [
        "No known allergies. Annual checkups up to date.",
        "Mild hypertension managed with medication. No drug allergies.",
        "Type 2 Diabetes diagnosed 2018. Currently on metformin.",
        "Asthma (mild). Uses inhaler as needed. No other conditions.",
        "No significant medical history. Occasional migraines.",
    ]

    created = []
    from datetime import datetime
    for i, (uname, first, last, dob, gender, blood, phone, addr) in enumerate(patients_data):
        u = User(
            username=uname,
            email=f"{uname}@email.com",
            first_name=first, last_name=last, role="patient"
        )
        u.set_password("Patient@1234")
        db.session.add(u)
        db.session.flush()

        p = Patient(
            user_id=u.id,
            date_of_birth=datetime.strptime(dob, "%Y-%m-%d").date(),
            gender=gender, blood_type=blood, phone=phone, address=addr,
            emergency_contact=f"Emergency — {phone}",
            medical_history=medical_histories[i],
        )
        db.session.add(p)
        created.append(p)

    db.session.flush()
    print(f"✅ Created {len(created)} patients  →  password: Patient@1234")
    return created


def seed_appointments(doctors, patients):
    """Create 20 sample appointments across various statuses."""
    today = date.today()
    reasons = [
        "Routine annual checkup",
        "Chest pain and shortness of breath",
        "Follow-up for hypertension management",
        "Persistent headaches for 2 weeks",
        "Knee pain after sports injury",
        "Skin rash present for 10 days",
        "Child vaccination and growth check",
        "Back pain radiating to left leg",
        "Irregular heartbeat episodes",
        "General fatigue and dizziness",
    ]
    notes_completed = [
        "Patient in good health. Blood pressure normal. Continue current medications.",
        "ECG performed. Mild arrhythmia detected. Referred to cardiology.",
        "Blood pressure well controlled. Schedule follow-up in 3 months.",
        "Migraine confirmed. Prescribed sumatriptan. Advised to track triggers.",
        "MRI ordered for knee. Possible meniscus tear. Physio referral given.",
    ]

    appointments = [
        # (patient_idx, doctor_idx, date_offset, time, status, reason, notes)
        # Past completed
        (0, 0, -30, "09:00", "completed", reasons[0], notes_completed[0]),
        (1, 1, -20, "10:00", "completed", reasons[1], notes_completed[1]),
        (2, 2, -15, "14:00", "completed", reasons[2], notes_completed[2]),
        (3, 3, -10, "11:00", "completed", reasons[3], notes_completed[3]),
        (4, 4, -7,  "15:00", "completed", reasons[4], notes_completed[4]),
        # Past cancelled
        (0, 1, -5,  "09:30", "cancelled", reasons[5], None),
        (1, 2, -3,  "10:30", "cancelled", reasons[6], None),
        # Today confirmed
        (2, 3,  0,  "10:00", "confirmed", reasons[7], None),
        (3, 4,  0,  "14:30", "confirmed", reasons[8], None),
        # Today pending
        (4, 0,  0,  "16:00", "pending",   reasons[9], None),
        # Upcoming confirmed
        (0, 1,  2,  "09:00", "confirmed", reasons[0], None),
        (1, 2,  3,  "10:00", "confirmed", reasons[1], None),
        (2, 3,  4,  "11:00", "confirmed", reasons[2], None),
        # Upcoming pending
        (3, 4,  5,  "09:30", "pending",   reasons[3], None),
        (4, 0,  6,  "14:00", "pending",   reasons[4], None),
        (0, 1,  7,  "15:00", "pending",   reasons[5], None),
        (1, 2,  8,  "10:30", "pending",   reasons[6], None),
        (2, 3, 10,  "09:00", "pending",   reasons[7], None),
        (3, 4, 12,  "14:30", "pending",   reasons[8], None),
        (4, 0, 14,  "16:00", "pending",   reasons[9], None),
    ]

    count = 0
    for pat_i, doc_i, day_offset, time, status, reason, notes in appointments:
        a = Appointment(
            patient_id=patients[pat_i % len(patients)].id,
            doctor_id=doctors[doc_i % len(doctors)].id,
            appointment_date=today + timedelta(days=day_offset),
            appointment_time=time,
            status=status,
            reason=reason,
            notes=notes,
        )
        db.session.add(a)
        count += 1

    db.session.commit()
    print(f"✅ Created {count} appointments (various statuses)")


def main():
    print("\n🏥  Hospital System — Database Seeder")
    print("=" * 48)
    with app.app_context():
        clear_data()
        seed_admin()
        depts   = seed_departments()
        doctors  = seed_doctors(depts)
        patients = seed_patients()
        seed_appointments(doctors, patients)
        print("=" * 48)
        print("🎉  Seeded successfully!\n")
        print("  Admin    →  admin@hospital.com      / Admin@1234")
        print("  Doctors  →  dr.surya@hospital.com   / Doctor@1234")
        print("  Patients →  surya_p@email.com        / Patient@1234")
        print(f"\n  Run: python run.py  →  http://127.0.0.1:5000\n")


if __name__ == "__main__":
    main()
