"""
Attendance model.
Records whether a student was present, absent, late, or on leave
for a specific date.
"""
from datetime import datetime, timezone
from ..extensions import db

# Valid status values for an attendance record
VALID_STATUSES = {"Present", "Absent", "Late", "Leave"}


class Attendance(db.Model):
    """Database model for a single student attendance record."""

    __tablename__ = "attendance"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking to the student
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Date of the attendance record (stored as Python date)
    date = db.Column(db.Date, nullable=False)

    # Attendance status — must be one of VALID_STATUSES
    status = db.Column(db.String(10), nullable=False, default="Absent")

    # Optional check-in / check-out times stored as strings "HH:MM"
    check_in = db.Column(db.String(5), nullable=True)   # e.g. "09:05"
    check_out = db.Column(db.String(5), nullable=True)  # e.g. "13:10"

    # Optional free-text remarks (e.g. reason for absence)
    remarks = db.Column(db.String(255), nullable=True)

    # Timestamp when the record was created
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Enforce one attendance record per student per day at the database level
    __table_args__ = (
        db.UniqueConstraint("student_id", "date", name="uq_student_date"),
    )

    # Relationship back to the Student model
    student = db.relationship("Student", back_populates="attendance_records")

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of this attendance record."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "student_code": self.student.student_id if self.student else None,
            "date": self.date.isoformat() if self.date else None,
            "status": self.status,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Attendance student={self.student_id} date={self.date} status={self.status}>"
