"""
Students API blueprint.
Provides CRUD endpoints for student records.

Prefix: /api/students  (registered in app factory)
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.student import Student
from ..schemas.student import student_schema, students_schema

students_bp = Blueprint("students", __name__)


# ─────────────────────────────────────────────────────────
# GET /api/students  — list all students (with optional search)
# ─────────────────────────────────────────────────────────
@students_bp.route("", methods=["GET"])
def get_students():
    """Return all students. Supports ?search= query param."""
    search = request.args.get("search", "").strip()

    query = Student.query

    if search:
        # Case-insensitive search across name, student_id, department, email
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Student.name.ilike(like),
                Student.student_id.ilike(like),
                Student.department.ilike(like),
                Student.email.ilike(like),
            )
        )

    students = query.order_by(Student.name).all()
    return jsonify({
        "success": True,
        "data": students_schema.dump(students),
        "total": len(students),
    }), 200


# ─────────────────────────────────────────────────────────
# GET /api/students/<id>  — get single student
# ─────────────────────────────────────────────────────────
@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id: int):
    """Return a single student by primary key id."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    return jsonify({"success": True, "data": student_schema.dump(student)}), 200


# ─────────────────────────────────────────────────────────
# POST /api/students  — create new student
# ─────────────────────────────────────────────────────────
@students_bp.route("", methods=["POST"])
def create_student():
    """Create a new student record."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    # Validate input
    try:
        data = student_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    # Check for duplicate student_id
    if Student.query.filter_by(student_id=data["student_id"]).first():
        return jsonify({"success": False, "message": f"Student ID '{data['student_id']}' already exists"}), 409

    # Check for duplicate email
    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "message": f"Email '{data['email']}' already exists"}), 409

    student = Student(**data)
    db.session.add(student)
    db.session.commit()

    return jsonify({"success": True, "message": "Student created", "data": student_schema.dump(student)}), 201


# ─────────────────────────────────────────────────────────
# PUT /api/students/<id>  — update student
# ─────────────────────────────────────────────────────────
@students_bp.route("/<int:student_id>", methods=["PUT"])
def update_student(student_id: int):
    """Update an existing student record."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"success": False, "message": "No JSON data provided"}), 400

    # Allow partial update — only load provided fields
    try:
        data = student_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"success": False, "message": "Validation error", "errors": err.messages}), 400

    # Check uniqueness of student_id if it is being changed
    new_sid = data.get("student_id")
    if new_sid and new_sid != student.student_id:
        if Student.query.filter_by(student_id=new_sid).first():
            return jsonify({"success": False, "message": f"Student ID '{new_sid}' already exists"}), 409

    # Check uniqueness of email if it is being changed
    new_email = data.get("email")
    if new_email and new_email != student.email:
        if Student.query.filter_by(email=new_email).first():
            return jsonify({"success": False, "message": f"Email '{new_email}' already exists"}), 409

    # Apply changes
    for key, value in data.items():
        setattr(student, key, value)

    db.session.commit()
    return jsonify({"success": True, "message": "Student updated", "data": student_schema.dump(student)}), 200


# ─────────────────────────────────────────────────────────
# DELETE /api/students/<id>  — delete student
# ─────────────────────────────────────────────────────────
@students_bp.route("/<int:student_id>", methods=["DELETE"])
def delete_student(student_id: int):
    """Delete a student and all their attendance records."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"success": True, "message": "Student deleted"}), 200
