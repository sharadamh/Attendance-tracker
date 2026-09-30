"""
Views blueprint — serves all HTML page templates.
Every route here simply renders a template; the frontend JS handles data via the API.
"""
from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    """Dashboard / home page."""
    return render_template("index.html")


@views_bp.route("/students")
def students():
    """Students management page."""
    return render_template("students.html")


@views_bp.route("/employees")
def employees():
    """Employees management page."""
    return render_template("employees.html")


@views_bp.route("/attendance")
def attendance():
    """Attendance marking page."""
    return render_template("attendance.html")


@views_bp.route("/reports")
def reports():
    """Reports page."""
    return render_template("reports.html")
