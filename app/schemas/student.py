"""
Marshmallow schema for the Student model.
Used for serialisation (model → JSON) and deserialisation (JSON → validated data).
"""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError


class StudentSchema(Schema):
    """Schema for Student serialisation and validation."""

    # Read-only fields (set by the server)
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Required fields
    student_id = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    department = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    semester = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    section = fields.Str(required=True, validate=validate.Length(min=1, max=10))

    # Optional fields
    phone = fields.Str(load_default=None, validate=validate.Length(max=20))

    @validates("email")
    def validate_email_format(self, value: str) -> None:
        """Extra email format check beyond the basic fields.Email()."""
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, value):
            raise ValidationError("Invalid email address format.")


# Convenience instances used in route handlers
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
