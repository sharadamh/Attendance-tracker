from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.employee import Shift, ShiftAssignment, Employee
from ..schemas.employee_schema import shift_schema, shifts_schema
from marshmallow import ValidationError

bp = Blueprint("shifts", __name__)


@bp.route("/shifts", methods=["GET"])
def list_shifts():
    shifts = Shift.query.all()
    return jsonify(shifts_schema.dump(shifts)), 200


@bp.route("/shifts/<int:shift_id>", methods=["GET"])
def get_shift(shift_id):
    shift = db.get_or_404(Shift, shift_id)
    return jsonify(shift_schema.dump(shift)), 200


@bp.route("/shifts", methods=["POST"])
def create_shift():
    try:
        data = shift_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    shift = Shift(**data)
    db.session.add(shift)
    db.session.commit()
    return jsonify(shift_schema.dump(shift)), 201


@bp.route("/shifts/<int:shift_id>", methods=["PUT"])
def update_shift(shift_id):
    shift = db.get_or_404(Shift, shift_id)
    try:
        data = shift_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for key, value in data.items():
        setattr(shift, key, value)
    db.session.commit()
    return jsonify(shift_schema.dump(shift)), 200


@bp.route("/shifts/<int:shift_id>", methods=["DELETE"])
def delete_shift(shift_id):
    shift = db.get_or_404(Shift, shift_id)
    db.session.delete(shift)
    db.session.commit()
    return jsonify({"message": "Shift deleted"}), 200


@bp.route("/shifts/<int:shift_id>/assign", methods=["POST"])
def assign_employee(shift_id):
    shift = db.get_or_404(Shift, shift_id)
    body = request.get_json() or {}
    employee_id = body.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400

    employee = db.get_or_404(Employee, employee_id)
    existing = ShiftAssignment.query.filter_by(
        employee_id=employee.id, shift_id=shift.id
    ).first()
    if existing:
        return jsonify({"error": "Employee already assigned to this shift"}), 409

    assignment = ShiftAssignment(employee_id=employee.id, shift_id=shift.id)
    db.session.add(assignment)
    db.session.commit()
    return jsonify({"message": "Assigned", "employee_id": employee.id, "shift_id": shift.id}), 201
