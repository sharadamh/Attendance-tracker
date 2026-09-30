"""
Marshmallow schema for the Employee model.
"""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError


class EmployeeSchema(Schema):
    """Schema for Employee serialisation and validation."""

    # Read-only fields
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Required fields
    employee_id = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    department = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    designation = fields.Str(required=True, validate=validate.Length(min=1, max=100))

    # Optional fields
    phone = fields.Str(load_default=None, validate=validate.Length(max=20))

    @validates("email")
    def validate_email_format(self, value: str) -> None:
        """Extra email format check."""
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, value):
            raise ValidationError("Invalid email address format.")


# Convenience instances used in route handlers
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
