"""
seed.py — populate the database with realistic sample data.

Safe to run repeatedly — existing records are skipped (no duplicates created).

Run with:
    python seed.py
"""
import sys
import os

# Ensure the attendance_tracker package is importable when running from its own directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models.student import Student
from app.models.employee import Employee
from app.models.shift import Shift
from app.models.attendance import Attendance

# ── Sample data ──────────────────────────────────────────────────────────────

STUDENTS = [
    {"student_id": "STU001", "name": "Alice Johnson",   "email": "alice.johnson@college.edu",   "phone": "+1-555-0101", "department": "Computer Science",   "semester": 3,  "section": "A"},
    {"student_id": "STU002", "name": "Bob Martinez",    "email": "bob.martinez@college.edu",    "phone": "+1-555-0102", "department": "Computer Science",   "semester": 3,  "section": "A"},
    {"student_id": "STU003", "name": "Carol White",     "email": "carol.white@college.edu",     "phone": "+1-555-0103", "department": "Computer Science",   "semester": 5,  "section": "B"},
    {"student_id": "STU004", "name": "David Kim",       "email": "david.kim@college.edu",       "phone": "+1-555-0104", "department": "Mathematics",        "semester": 2,  "section": "A"},
    {"student_id": "STU005", "name": "Eva Rodriguez",   "email": "eva.rodriguez@college.edu",   "phone": "+1-555-0105", "department": "Mathematics",        "semester": 4,  "section": "B"},
    {"student_id": "STU006", "name": "Frank Chen",      "email": "frank.chen@college.edu",      "phone": "+1-555-0106", "department": "Physics",            "semester": 1,  "section": "A"},
    {"student_id": "STU007", "name": "Grace Lee",       "email": "grace.lee@college.edu",       "phone": "+1-555-0107", "department": "Physics",            "semester": 3,  "section": "C"},
    {"student_id": "STU008", "name": "Henry Brown",     "email": "henry.brown@college.edu",     "phone": "+1-555-0108", "department": "Chemistry",          "semester": 6,  "section": "A"},
    {"student_id": "STU009", "name": "Iris Patel",      "email": "iris.patel@college.edu",      "phone": "+1-555-0109", "department": "Chemistry",          "semester": 2,  "section": "B"},
    {"student_id": "STU010", "name": "James Nguyen",    "email": "james.nguyen@college.edu",    "phone": "+1-555-0110", "department": "Computer Science",   "semester": 7,  "section": "A"},
    {"student_id": "STU011", "name": "Karen Smith",     "email": "karen.smith@college.edu",     "phone": "+1-555-0111", "department": "Mathematics",        "semester": 5,  "section": "A"},
    {"student_id": "STU012", "name": "Leo Turner",      "email": "leo.turner@college.edu",      "phone": "+1-555-0112", "department": "Physics",            "semester": 4,  "section": "B"},
]

EMPLOYEES = [
    {"employee_id": "EMP001", "name": "Dr. Sarah Connor",    "email": "s.connor@college.edu",    "phone": "+1-555-0201", "department": "Computer Science", "designation": "Professor"},
    {"employee_id": "EMP002", "name": "Prof. John Adams",    "email": "j.adams@college.edu",     "phone": "+1-555-0202", "department": "Mathematics",      "designation": "Associate Professor"},
    {"employee_id": "EMP003", "name": "Dr. Emily Clarke",    "email": "e.clarke@college.edu",    "phone": "+1-555-0203", "department": "Physics",          "designation": "Senior Lecturer"},
    {"employee_id": "EMP004", "name": "Mr. Robert Wilson",   "email": "r.wilson@college.edu",    "phone": "+1-555-0204", "department": "Chemistry",        "designation": "Lecturer"},
    {"employee_id": "EMP005", "name": "Ms. Linda Thompson",  "email": "l.thompson@college.edu",  "phone": "+1-555-0205", "department": "Administration",   "designation": "Administrative Officer"},
]

SHIFTS = [
    {"name": "Morning",   "start_time": "09:00", "end_time": "13:00"},
    {"name": "Afternoon", "start_time": "14:00", "end_time": "17:00"},
]

# Generate attendance for the last 7 weekdays
def last_n_weekdays(n: int):
    """Return the last n weekday dates (Mon-Fri) in descending order."""
    days = []
    current = date.today()
    while len(days) < n:
        if current.weekday() < 5:   # 0-4 = Mon-Fri
            days.append(current)
        current -= timedelta(days=1)
    return days


def seed():
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("Attendance Tracker - Seed Script")
        print("=" * 50)

        # ── Shifts ──────────────────────────────────────────
        shift_count = 0
        for s_data in SHIFTS:
            if not Shift.query.filter_by(name=s_data["name"]).first():
                db.session.add(Shift(**s_data))
                shift_count += 1
        db.session.commit()
        print(f"[+] Shifts:    {shift_count} new  ({Shift.query.count()} total)")

        # ── Students ─────────────────────────────────────────
        student_count = 0
        for s_data in STUDENTS:
            if not Student.query.filter_by(student_id=s_data["student_id"]).first():
                db.session.add(Student(**s_data))
                student_count += 1
        db.session.commit()
        print(f"[+] Students:  {student_count} new  ({Student.query.count()} total)")

        # ── Employees ────────────────────────────────────────
        emp_count = 0
        for e_data in EMPLOYEES:
            if not Employee.query.filter_by(employee_id=e_data["employee_id"]).first():
                db.session.add(Employee(**e_data))
                emp_count += 1
        db.session.commit()
        print(f"[+] Employees: {emp_count} new  ({Employee.query.count()} total)")

        # ── Attendance ───────────────────────────────────────
        # Create attendance for all students over the last 7 weekdays
        # with a realistic mix of statuses
        import random
        random.seed(42)

        students = Student.query.all()
        weekdays = last_n_weekdays(7)

        # Status distribution: mostly Present, some Absent/Late/Leave
        STATUS_WEIGHTS = ["Present"] * 7 + ["Absent"] * 2 + ["Late"] + ["Leave"]

        att_count = 0
        for student in students:
            for att_date in weekdays:
                existing = Attendance.query.filter_by(
                    student_id=student.id, date=att_date
                ).first()
                if existing:
                    continue

                status = random.choice(STATUS_WEIGHTS)
                check_in  = None
                check_out = None

                if status in ("Present", "Late"):
                    hour_in  = 9 if status == "Present" else random.randint(9, 10)
                    minute_in = random.randint(0, 30) if status == "Late" else random.randint(0, 10)
                    check_in  = f"{hour_in:02d}:{minute_in:02d}"
                    check_out = f"{random.randint(13, 14):02d}:{random.randint(0,59):02d}"

                record = Attendance(
                    student_id=student.id,
                    date=att_date,
                    status=status,
                    check_in=check_in,
                    check_out=check_out,
                    remarks=None,
                )
                db.session.add(record)
                att_count += 1

        db.session.commit()
        print(f"[+] Attendance: {att_count} new  ({Attendance.query.count()} total)")
        print("=" * 50)
        print("Seed complete! Run: python run.py")
        print("Open:           http://127.0.0.1:5000")
        print("=" * 50)


if __name__ == "__main__":
    seed()
