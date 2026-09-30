# Attendance Tracker

A full-stack **Attendance Tracker** web application built with **Flask** (Python) and **Vanilla JavaScript**.  
Manage students, employees, and daily attendance records with a clean sidebar-based UI and a RESTful JSON API.

---

## Features

- **Dashboard** — real-time stats (total students/employees, present/absent today, attendance %)
- **Student Management** — full CRUD with search
- **Employee Management** — full CRUD with search
- **Attendance Tracking** — mark Present / Absent / Late / Leave with check-in/out times
- **Reports** — filterable detail report + per-student summary with attendance % calculation
- **CSV Export** — download attendance reports as CSV
- **Print-friendly** reports
- **Duplicate prevention** — one attendance record per student per day (enforced in API + database)
- **Validation** — required fields, email format, duplicate IDs, invalid statuses
- **Seed data** — 12 students, 5 employees, 2 shifts, ~84 attendance records

---

## Technologies

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python 3, Flask 3.0.3               |
| ORM       | Flask-SQLAlchemy 3.1.1              |
| Migrations| Flask-Migrate 4.0.7                 |
| Schemas   | Marshmallow 3.21.3                  |
| Config    | python-dotenv 1.0.1                 |
| Database  | SQLite (file: `instance/attendance.db`) |
| Frontend  | HTML5, CSS3, Vanilla JavaScript     |
| Tests     | pytest 8.2.2                        |

---

## Project Structure

```
attendance_tracker/
│
├── run.py                  ← Application entry point
├── seed.py                 ← Sample data loader
├── requirements.txt
├── .env.example
├── README.md
│
├── app/
│   ├── __init__.py         ← Application factory
│   ├── config.py           ← Configuration classes
│   ├── extensions.py       ← db / migrate instances
│   │
│   ├── models/
│   │   ├── student.py
│   │   ├── employee.py
│   │   ├── attendance.py
│   │   └── shift.py
│   │
│   ├── routes/
│   │   ├── views.py        ← HTML page routes
│   │   ├── students.py
│   │   ├── employees.py
│   │   ├── attendance.py
│   │   └── reports.py
│   │
│   ├── schemas/
│   │   ├── student.py
│   │   ├── employee.py
│   │   └── attendance.py
│   │
│   └── templates/
│       ├── base.html
│       ├── index.html      ← Dashboard
│       ├── students.html
│       ├── employees.html
│       ├── attendance.html
│       └── reports.html
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
└── tests/
    ├── conftest.py
    ├── test_students.py
    ├── test_employees.py
    ├── test_attendance.py
    └── test_reports.py
```

---

## Installation (Windows PowerShell)

### 1. Create and activate a virtual environment

```powershell
cd attendance_tracker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If PowerShell blocks script execution, run the following once as Administrator:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Alternatively, run scripts directly without activating:
> ```powershell
> .\.venv\Scripts\python.exe seed.py
> .\.venv\Scripts\python.exe run.py
> ```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment (optional)

```powershell
Copy-Item .env.example .env
# Edit .env to change SECRET_KEY if needed
```

### 4. Initialize the database

The database is created automatically when the application first starts.  
Alternatively, initialise it explicitly:

```powershell
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. Load seed data

```powershell
python seed.py
```

### 6. Start the application

```powershell
python run.py
```

### 7. Open the application

```
http://127.0.0.1:5000
```

---

## API Endpoints

### Students

| Method | Endpoint                 | Description           |
|--------|--------------------------|-----------------------|
| GET    | `/api/students`          | List all students     |
| GET    | `/api/students/<id>`     | Get student by ID     |
| POST   | `/api/students`          | Create student        |
| PUT    | `/api/students/<id>`     | Update student        |
| DELETE | `/api/students/<id>`     | Delete student        |

Query params: `?search=<text>`

### Employees

| Method | Endpoint                 | Description           |
|--------|--------------------------|-----------------------|
| GET    | `/api/employees`         | List all employees    |
| GET    | `/api/employees/<id>`    | Get employee by ID    |
| POST   | `/api/employees`         | Create employee       |
| PUT    | `/api/employees/<id>`    | Update employee       |
| DELETE | `/api/employees/<id>`    | Delete employee       |

Query params: `?search=<text>`

### Attendance

| Method | Endpoint                  | Description                |
|--------|---------------------------|----------------------------|
| GET    | `/api/attendance`         | List attendance records    |
| POST   | `/api/attendance`         | Mark attendance            |
| PUT    | `/api/attendance/<id>`    | Update attendance record   |
| DELETE | `/api/attendance/<id>`    | Delete attendance record   |

Query params: `?date=YYYY-MM-DD`, `?student_id=<int>`, `?status=<str>`

### Reports

| Method | Endpoint                       | Description                        |
|--------|--------------------------------|------------------------------------|
| GET    | `/api/reports/attendance`      | Filtered attendance detail report  |
| GET    | `/api/reports/summary`         | Per-student attendance summary     |
| GET    | `/api/reports/dashboard`       | Dashboard stats                    |

Query params: `?date_from=`, `?date_to=`, `?department=`, `?status=`, `?format=csv`

---

## Running Tests

```powershell
pytest tests/ -v
```

Or with a coverage summary:

```powershell
pytest tests/ -v --tb=short
```

---

## API Response Format

All API responses follow this structure:

**Success:**
```json
{
    "success": true,
    "data": { ... },
    "message": "Operation completed"
}
```

**Error:**
```json
{
    "success": false,
    "message": "Description of the error"
}
```

---

## HTTP Status Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 200  | OK                                   |
| 201  | Created                              |
| 400  | Bad Request (validation error)       |
| 404  | Not Found                            |
| 409  | Conflict (duplicate record)          |
| 500  | Internal Server Error                |

---

## Attendance Status Values

- **Present** — student was present on time
- **Late** — student arrived late (counts as present in percentage)
- **Absent** — student was absent
- **Leave** — student was on approved leave

---

## Attendance Percentage Formula

```
attendance_percentage = (present + late) / total_working_days × 100
```

---

## Notes

- The SQLite database file is created at `instance/attendance.db` on first run.
- The seed script is idempotent — running it multiple times will not create duplicate records.
- Flask-Migrate is included for future schema migrations (`flask db init`, `flask db migrate`, `flask db upgrade`).
