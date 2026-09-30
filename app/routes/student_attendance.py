from flask import Blueprint, request, jsonify
from datetime import date as date_type
from ..extensions import db
from ..models.student import StudentAttendance, AttendanceStatus
from ..schemas.student_schema import attendance_schema, attendances_schema
from marshmallow import ValidationError

bp = Blueprint("student_attendance", __name__)


@bp.route("/attendance/student", methods=["POST"])
def mark_student_attendance():
    try:
        data = attendance_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    record = StudentAttendance(
        student_id=data["student_id"],
        class_id=data["class_id"],
        date=data["date"],
        status=AttendanceStatus(data["status"]),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(attendance_schema.dump(record)), 201


@bp.route("/attendance/student", methods=["GET"])
def query_student_attendance():
    class_id = request.args.get("class_id", type=int)
    student_id = request.args.get("student_id", type=int)
    date_str = request.args.get("date")

    query = StudentAttendance.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    if student_id:
        query = query.filter_by(student_id=student_id)
    if date_str:
        try:
            d = date_type.fromisoformat(date_str)
            query = query.filter_by(date=d)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    records = query.all()
    return jsonify(attendances_schema.dump(records)), 200
