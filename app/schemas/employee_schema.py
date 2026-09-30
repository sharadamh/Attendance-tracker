from marshmallow import Schema, fields, validate


class EmployeeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    email = fields.Email(required=True)
    department = fields.Str(load_default=None)
    role = fields.Str(load_default=None)


class ShiftSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    date = fields.Date(required=True)


class EmployeeAttendanceSchema(Schema):
    id = fields.Int(dump_only=True)
    employee_id = fields.Int(required=True)
    shift_id = fields.Int(required=True)
    date = fields.Date(required=True)
    status = fields.Function(
        serialize=lambda obj: obj.status.value if hasattr(obj.status, "value") else obj.status,
        deserialize=lambda v: v,
        required=True,
        validate=validate.OneOf(["present", "absent", "late"]),
    )


employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
shift_schema = ShiftSchema()
shifts_schema = ShiftSchema(many=True)
attendance_schema = EmployeeAttendanceSchema()
attendances_schema = EmployeeAttendanceSchema(many=True)
