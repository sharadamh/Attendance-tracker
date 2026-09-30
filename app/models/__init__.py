"""
Models package — exposes all models for easy import.
"""
from .student import Student
from .employee import Employee
from .shift import Shift
from .attendance import Attendance

__all__ = ["Student", "Employee", "Shift", "Attendance"]
