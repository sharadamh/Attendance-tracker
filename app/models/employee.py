"""
Employee model.
Represents a staff / faculty member employed at the institution.
"""
from datetime import datetime, timezone
from ..extensions import db


class Employee(db.Model):
    """Database model for an employee."""

    __tablename__ = "employees"

    # Primary key (auto-incremented)
    id = db.Column(db.Integer, primary_key=True)

    # Unique institutional employee identifier (e.g. "EMP001")
    employee_id = db.Column(db.String(20), unique=True, nullable=False)

    # Full name of the employee
    name = db.Column(db.String(100), nullable=False)

    # Contact details
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    # Professional information
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)

    # Record timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of this employee."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "designation": self.designation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Employee {self.employee_id} – {self.name}>"
