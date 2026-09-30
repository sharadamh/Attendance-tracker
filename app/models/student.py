"""
Student model.
Represents a student enrolled in the institution.
"""
from datetime import datetime, timezone
from ..extensions import db


class Student(db.Model):
    """Database model for a student."""

    __tablename__ = "students"

    # Primary key (auto-incremented)
    id = db.Column(db.Integer, primary_key=True)

    # Unique institutional student identifier (e.g. "STU001")
    student_id = db.Column(db.String(20), unique=True, nullable=False)

    # Full name of the student
    name = db.Column(db.String(100), nullable=False)

    # Contact details
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    # Academic information
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)

    # Record timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationship: one student → many attendance records
    # cascade="all, delete-orphan" removes attendance records when student is deleted
    attendance_records = db.relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of this student."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "semester": self.semester,
            "section": self.section,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Student {self.student_id} – {self.name}>"
