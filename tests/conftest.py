"""
Shared pytest fixtures.
These are automatically discovered by pytest and made available to all test modules.
"""
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create application with in-memory SQLite database for the test session."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Flask test client — one per test function."""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Wipe all table rows between tests to keep tests independent."""
    with app.app_context():
        yield
        _db.session.remove()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


# ── Helpers to create common test objects ──────────────────────────────────

def make_student(client, overrides=None):
    """POST a valid student and return the response JSON."""
    data = {
        "student_id": "STU-T1",
        "name": "Test Student",
        "email": "test.student@test.edu",
        "department": "Computer Science",
        "semester": 3,
        "section": "A",
    }
    if overrides:
        data.update(overrides)
    return client.post("/api/students", json=data)


def make_employee(client, overrides=None):
    """POST a valid employee and return the response JSON."""
    data = {
        "employee_id": "EMP-T1",
        "name": "Test Employee",
        "email": "test.employee@test.edu",
        "department": "Computer Science",
        "designation": "Lecturer",
    }
    if overrides:
        data.update(overrides)
    return client.post("/api/employees", json=data)
