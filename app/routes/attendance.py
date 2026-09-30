"""
Attendance API blueprint.
Provides endpoints to create, read, update, and delete attendance records.

Prefix: /api/attendance  (registered in app factory)
"""
from datetime import date as date_type
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.attendance import Attendance
from ..models.student import Student
from ..schemas.attendance import attendance_schema, attendances_schema

attendance_bp = Blueprint("attendance", __name__)


# ─────────────────────────────────────────────────────────
# GET /api/attendance  — list attendance records
# ─────────────────────────────────────────────────────────
@attendance_bp.route("", methods=["GET"])
def get_attendance():
    """
    Return attendance records.
    Supports optional query params:
      ?date=YYYY-MM-DD
      ?student_id=<int>
      ?status=Present|Absent|Late|Leave
    """
    query = Attendance.query.join(Student)

    # Filter by specific date
    date_str = request.args.get("date")
    if date_str:
        try:
            filter_date = date_type.fromisoformat(date_str)
            query = query.filter(Attendance.date == filter_date)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Filter by student
    student_id = request.args.get("student_id")
    if student_id:
        query = query.filter(Attendance.student_id == int(student_id))

    # Filter by status
    status = request.args.get("status")
    if status:
        query = query.filter(Attendance.status == status)

    records = query.order_by(Attendance.date.desc()).all()
    return jsonify({
        "success": True,
        "data": attendances_schema.dump(records),
        "total": len(records),
    }), 200


# ─────────────────────────────────────────────────────────
# POST /api/attendance  — create attendance record
# ─────────────────────────────────────────────────────────
@attendance_bp.route("", methods=["POST"])
def create_attendance():
    """Mark attendance for a student on a specific date."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    try:
        data = attendance_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    # Verify the student exists
    student = db.session.get(Student, data["student_id"])
    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    # Check for duplicate: same student + same date
    existing = Attendance.query.filter_by(
        student_id=data["student_id"], date=data["date"]
    ).first()
    if existing:
        return jsonify({
            "success": False,
            "message": f"Attendance for this student on {data['date']} already exists"
        }), 409

    record = Attendance(**data)
    db.session.add(record)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Duplicate attendance record (database constraint)"
        }), 409

    return jsonify({
        "success": True,
        "message": "Attendance marked",
        "data": attendance_schema.dump(record),
    }), 201


# ─────────────────────────────────────────────────────────
# PUT /api/attendance/<id>  — update attendance record
# ─────────────────────────────────────────────────────────
@attendance_bp.route("/<int:record_id>", methods=["PUT"])
def update_attendance(record_id: int):
    """Update an existing attendance record."""
    record = db.session.get(Attendance, record_id)
    if not record:
        return jsonify({"success": False, "message": "Attendance record not found"}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    try:
        data = attendance_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    # If student_id or date is changing, check for duplicate
    new_sid = data.get("student_id", record.student_id)
    new_date = data.get("date", record.date)

    if new_sid != record.student_id or new_date != record.date:
        conflict = Attendance.query.filter_by(
            student_id=new_sid, date=new_date
        ).filter(Attendance.id != record_id).first()
        if conflict:
            return jsonify({
                "success": False,
                "message": "Another attendance record already exists for this student on that date"
            }), 409

    for key, value in data.items():
        setattr(record, key, value)

    db.session.commit()
    return jsonify({"success": True, "message": "Attendance updated", "data": attendance_schema.dump(record)}), 200


# ─────────────────────────────────────────────────────────
# DELETE /api/attendance/<id>  — delete attendance record
# ─────────────────────────────────────────────────────────
@attendance_bp.route("/<int:record_id>", methods=["DELETE"])
def delete_attendance(record_id: int):
    """Delete a single attendance record."""
    record = db.session.get(Attendance, record_id)
    if not record:
        return jsonify({"success": False, "message": "Attendance record not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True, "message": "Attendance record deleted"}), 200
