"""
Reports API blueprint.
Provides filtered attendance report and summary endpoints.

Prefix: /api/reports  (registered in app factory)
"""
import csv
import io
from datetime import date as date_type
from flask import Blueprint, request, jsonify, Response

from ..extensions import db
from ..models.attendance import Attendance
from ..models.student import Student

reports_bp = Blueprint("reports", __name__)


def _parse_date(value: str, field_name: str):
    """Parse a date string; return (date, error_response) tuple."""
    try:
        return date_type.fromisoformat(value), None
    except ValueError:
        return None, (
            jsonify({"success": False, "message": f"Invalid {field_name} format. Use YYYY-MM-DD"}),
            400,
        )


# ─────────────────────────────────────────────────────────
# GET /api/reports/attendance  — detailed filtered report
# ─────────────────────────────────────────────────────────
@reports_bp.route("/attendance", methods=["GET"])
def attendance_report():
    """
    Return filtered attendance records.

    Query params (all optional):
      date_from=YYYY-MM-DD
      date_to=YYYY-MM-DD
      student_id=<int>
      department=<str>
      status=Present|Absent|Late|Leave
      format=csv   (returns CSV file download)
    """
    query = Attendance.query.join(Student)

    # ── Date range filter ──
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    if date_from_str:
        date_from, err = _parse_date(date_from_str, "date_from")
        if err:
            return err
        query = query.filter(Attendance.date >= date_from)

    if date_to_str:
        date_to, err = _parse_date(date_to_str, "date_to")
        if err:
            return err
        query = query.filter(Attendance.date <= date_to)

    # ── Student filter ──
    student_id = request.args.get("student_id")
    if student_id:
        try:
            query = query.filter(Attendance.student_id == int(student_id))
        except ValueError:
            return jsonify({"success": False, "message": "Invalid student_id"}), 400

    # ── Department filter ──
    department = request.args.get("department")
    if department:
        query = query.filter(Student.department.ilike(f"%{department}%"))

    # ── Status filter ──
    status = request.args.get("status")
    if status:
        query = query.filter(Attendance.status == status)

    records = query.order_by(Attendance.date.desc(), Student.name).all()

    # ── CSV export ──
    if request.args.get("format") == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Student ID", "Name", "Department", "Date",
            "Status", "Check In", "Check Out", "Remarks"
        ])
        for r in records:
            writer.writerow([
                r.student.student_id,
                r.student.name,
                r.student.department,
                r.date.isoformat(),
                r.status,
                r.check_in or "",
                r.check_out or "",
                r.remarks or "",
            ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=attendance_report.csv"},
        )

    # ── JSON response ──
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "student_id": r.student.student_id,
            "student_name": r.student.name,
            "department": r.student.department,
            "date": r.date.isoformat(),
            "status": r.status,
            "check_in": r.check_in,
            "check_out": r.check_out,
            "remarks": r.remarks,
        })

    return jsonify({"success": True, "data": data, "total": len(data)}), 200


# ─────────────────────────────────────────────────────────
# GET /api/reports/summary  — per-student attendance summary
# ─────────────────────────────────────────────────────────
@reports_bp.route("/summary", methods=["GET"])
def attendance_summary():
    """
    Return per-student attendance summary.

    Query params (all optional):
      date_from=YYYY-MM-DD
      date_to=YYYY-MM-DD
      department=<str>
    """
    # Build base query
    att_query = db.session.query(Attendance).join(Student)

    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")
    department = request.args.get("department")

    if date_from_str:
        date_from, err = _parse_date(date_from_str, "date_from")
        if err:
            return err
        att_query = att_query.filter(Attendance.date >= date_from)

    if date_to_str:
        date_to, err = _parse_date(date_to_str, "date_to")
        if err:
            return err
        att_query = att_query.filter(Attendance.date <= date_to)

    if department:
        att_query = att_query.filter(Student.department.ilike(f"%{department}%"))

    records = att_query.all()

    # Group records by student
    student_stats: dict = {}
    for r in records:
        sid = r.student_id
        if sid not in student_stats:
            student_stats[sid] = {
                "student_id": r.student.student_id,
                "name": r.student.name,
                "department": r.student.department,
                "total": 0,
                "present": 0,
                "absent": 0,
                "late": 0,
                "leave": 0,
            }
        student_stats[sid]["total"] += 1
        status_key = r.status.lower()
        if status_key in student_stats[sid]:
            student_stats[sid][status_key] += 1

    # Calculate attendance percentage for each student
    summary = []
    for stats in student_stats.values():
        total = stats["total"]
        present = stats["present"] + stats["late"]   # late counts as present
        percentage = round((present / total * 100), 2) if total > 0 else 0.0
        summary.append({**stats, "attendance_percentage": percentage})

    # Sort by name
    summary.sort(key=lambda x: x["name"])

    return jsonify({"success": True, "data": summary, "total": len(summary)}), 200


# ─────────────────────────────────────────────────────────
# GET /api/reports/dashboard  — dashboard stats
# ─────────────────────────────────────────────────────────
@reports_bp.route("/dashboard", methods=["GET"])
def dashboard_stats():
    """Return quick stats for the dashboard."""
    from ..models.employee import Employee

    today = date_type.today()

    total_students = Student.query.count()
    total_employees = Employee.query.count()

    # Today's attendance figures
    today_records = Attendance.query.filter_by(date=today).all()
    present_today = sum(1 for r in today_records if r.status in ("Present", "Late"))
    absent_today = sum(1 for r in today_records if r.status == "Absent")
    total_today = len(today_records)
    attendance_pct = round((present_today / total_today * 100), 1) if total_today > 0 else 0.0

    return jsonify({
        "success": True,
        "data": {
            "total_students": total_students,
            "total_employees": total_employees,
            "present_today": present_today,
            "absent_today": absent_today,
            "total_marked_today": total_today,
            "attendance_percentage": attendance_pct,
        },
    }), 200
