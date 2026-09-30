"""
Shift model.
Represents a time-block during which attendance can be marked.
Example: Morning (09:00-13:00), Afternoon (14:00-17:00).
"""
from ..extensions import db


class Shift(db.Model):
    """Database model for a work/study shift."""

    __tablename__ = "shifts"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Human-readable shift name (e.g. "Morning")
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Shift start and end stored as time strings "HH:MM"
    start_time = db.Column(db.String(5), nullable=False)   # e.g. "09:00"
    end_time = db.Column(db.String(5), nullable=False)     # e.g. "13:00"

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of this shift."""
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def __repr__(self) -> str:
        return f"<Shift {self.name} {self.start_time}-{self.end_time}>"
