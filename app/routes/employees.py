"""
Employees API blueprint.
Provides CRUD endpoints for employee records.

Prefix: /api/employees  (registered in app factory)
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..extensions import db
from ..models.employee import Employee
from ..schemas.employee import employee_schema, employees_schema

employees_bp = Blueprint("employees", __name__)


# ─────────────────────────────────────────────────────────
# GET /api/employees  — list all employees
# ─────────────────────────────────────────────────────────
@employees_bp.route("", methods=["GET"])
def get_employees():
    """Return all employees. Supports ?search= query param."""
    search = request.args.get("search", "").strip()
    query = Employee.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Employee.name.ilike(like),
                Employee.employee_id.ilike(like),
                Employee.department.ilike(like),
                Employee.designation.ilike(like),
                Employee.email.ilike(like),
            )
        )

    employees = query.order_by(Employee.name).all()
    return jsonify({
        "success": True,
        "data": employees_schema.dump(employees),
        "total": len(employees),
    }), 200


# ─────────────────────────────────────────────────────────
# GET /api/employees/<id>  — get single employee
# ─────────────────────────────────────────────────────────
@employees_bp.route("/<int:emp_id>", methods=["GET"])
def get_employee(emp_id: int):
    """Return a single employee by primary key id."""
    employee = db.session.get(Employee, emp_id)
    if not employee:
        return jsonify({"success": False, "message": "Employee not found"}), 404

    return jsonify({"success": True, "data": employee_schema.dump(employee)}), 200


# ─────────────────────────────────────────────────────────
# POST /api/employees  — create new employee
# ─────────────────────────────────────────────────────────
@employees_bp.route("", methods=["POST"])
def create_employee():
    """Create a new employee record."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    try:
        data = employee_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    if Employee.query.filter_by(employee_id=data["employee_id"]).first():
        return jsonify({"success": False, "message": f"Employee ID '{data['employee_id']}' already exists"}), 409

    if Employee.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "message": f"Email '{data['email']}' already exists"}), 409

    employee = Employee(**data)
    db.session.add(employee)
    db.session.commit()

    return jsonify({"success": True, "message": "Employee created", "data": employee_schema.dump(employee)}), 201


# ─────────────────────────────────────────────────────────
# PUT /api/employees/<id>  — update employee
# ─────────────────────────────────────────────────────────
@employees_bp.route("/<int:emp_id>", methods=["PUT"])
def update_employee(emp_id: int):
    """Update an existing employee record."""
    employee = db.session.get(Employee, emp_id)
    if not employee:
        return jsonify({"success": False, "message": "Employee not found"}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    try:
        data = employee_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    new_eid = data.get("employee_id")
    if new_eid and new_eid != employee.employee_id:
        if Employee.query.filter_by(employee_id=new_eid).first():
            return jsonify({"success": False, "message": f"Employee ID '{new_eid}' already exists"}), 409

    new_email = data.get("email")
    if new_email and new_email != employee.email:
        if Employee.query.filter_by(email=new_email).first():
            return jsonify({"success": False, "message": f"Email '{new_email}' already exists"}), 409

    for key, value in data.items():
        setattr(employee, key, value)

    db.session.commit()
    return jsonify({"success": True, "message": "Employee updated", "data": employee_schema.dump(employee)}), 200


# ─────────────────────────────────────────────────────────
# DELETE /api/employees/<id>  — delete employee
# ─────────────────────────────────────────────────────────
@employees_bp.route("/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id: int):
    """Delete an employee record."""
    employee = db.session.get(Employee, emp_id)
    if not employee:
        return jsonify({"success": False, "message": "Employee not found"}), 404

    db.session.delete(employee)
    db.session.commit()
    return jsonify({"success": True, "message": "Employee deleted"}), 200
