from flask import Blueprint, request, jsonify
from datetime import date as date_type
from ..extensions import db
from ..models.employee import EmployeeAttendance, EmployeeAttendanceStatus
from ..schemas.employee_schema import attendance_schema, attendances_schema
from marshmallow import ValidationError

bp = Blueprint("employee_attendance", __name__)


@bp.route("/attendance/employee", methods=["POST"])
def mark_employee_attendance():
    try:
        data = attendance_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    record = EmployeeAttendance(
        employee_id=data["employee_id"],
        shift_id=data["shift_id"],
        date=data["date"],
        status=EmployeeAttendanceStatus(data["status"]),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(attendance_schema.dump(record)), 201


@bp.route("/attendance/employee", methods=["GET"])
def query_employee_attendance():
    shift_id = request.args.get("shift_id", type=int)
    employee_id = request.args.get("employee_id", type=int)
    date_str = request.args.get("date")

    query = EmployeeAttendance.query
    if shift_id:
        query = query.filter_by(shift_id=shift_id)
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if date_str:
        try:
            d = date_type.fromisoformat(date_str)
            query = query.filter_by(date=d)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    records = query.all()
    return jsonify(attendances_schema.dump(records)), 200
