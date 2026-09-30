from marshmallow import Schema, fields, validate


class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    email = fields.Email(required=True)
    enrollment_number = fields.Str(required=True, validate=validate.Length(min=1, max=64))


class ClassSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    subject = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    instructor = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    schedule = fields.Str(load_default=None)


class StudentAttendanceSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    class_id = fields.Int(required=True)
    date = fields.Date(required=True)
    status = fields.Function(
        serialize=lambda obj: obj.status.value if hasattr(obj.status, "value") else obj.status,
        deserialize=lambda v: v,
        required=True,
        validate=validate.OneOf(["present", "absent", "late"]),
    )


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
class_schema = ClassSchema()
classes_schema = ClassSchema(many=True)
attendance_schema = StudentAttendanceSchema()
attendances_schema = StudentAttendanceSchema(many=True)
