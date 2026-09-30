"""
Marshmallow schema for the Attendance model.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from ..models.attendance import VALID_STATUSES


class AttendanceSchema(Schema):
    """Schema for Attendance serialisation and validation."""

    # Read-only fields
    id = fields.Int(dump_only=True)
    student_name = fields.Str(dump_only=True)
    student_code = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Required fields
    student_id = fields.Int(required=True)
    date = fields.Date(required=True, format="%Y-%m-%d")
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            list(VALID_STATUSES),
            error="Status must be one of: Present, Absent, Late, Leave"
        ),
    )

    # Optional fields
    check_in = fields.Str(
        load_default=None,
        validate=validate.Regexp(
            r"^\d{2}:\d{2}$", error="check_in must be in HH:MM format"
        ),
    )
    check_out = fields.Str(
        load_default=None,
        validate=validate.Regexp(
            r"^\d{2}:\d{2}$", error="check_out must be in HH:MM format"
        ),
    )
    remarks = fields.Str(load_default=None, validate=validate.Length(max=255))

    @validates("date")
    def validate_date_not_future(self, value) -> None:
        """Attendance cannot be marked for a future date."""
        from datetime import date
        if value > date.today():
            raise ValidationError("Attendance date cannot be in the future.")


# Convenience instances used in route handlers
attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
