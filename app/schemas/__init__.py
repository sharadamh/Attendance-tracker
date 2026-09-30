"""
Schemas package — exposes all Marshmallow schemas.
"""
from .student import StudentSchema, student_schema, students_schema
from .employee import EmployeeSchema, employee_schema, employees_schema
from .attendance import AttendanceSchema, attendance_schema, attendances_schema

__all__ = [
    "StudentSchema", "student_schema", "students_schema",
    "EmployeeSchema", "employee_schema", "employees_schema",
    "AttendanceSchema", "attendance_schema", "attendances_schema",
]
