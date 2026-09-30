from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.student import Class, ClassEnrollment, Student
from ..schemas.student_schema import class_schema, classes_schema
from marshmallow import ValidationError

bp = Blueprint("classes", __name__)


@bp.route("/classes", methods=["GET"])
def list_classes():
    classes = Class.query.all()
    return jsonify(classes_schema.dump(classes)), 200


@bp.route("/classes/<int:class_id>", methods=["GET"])
def get_class(class_id):
    cls = db.get_or_404(Class, class_id)
    return jsonify(class_schema.dump(cls)), 200


@bp.route("/classes", methods=["POST"])
def create_class():
    try:
        data = class_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    cls = Class(**data)
    db.session.add(cls)
    db.session.commit()
    return jsonify(class_schema.dump(cls)), 201


@bp.route("/classes/<int:class_id>", methods=["PUT"])
def update_class(class_id):
    cls = db.get_or_404(Class, class_id)
    try:
        data = class_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for key, value in data.items():
        setattr(cls, key, value)
    db.session.commit()
    return jsonify(class_schema.dump(cls)), 200


@bp.route("/classes/<int:class_id>", methods=["DELETE"])
def delete_class(class_id):
    cls = db.get_or_404(Class, class_id)
    db.session.delete(cls)
    db.session.commit()
    return jsonify({"message": "Class deleted"}), 200


@bp.route("/classes/<int:class_id>/enroll", methods=["POST"])
def enroll_student(class_id):
    cls = db.get_or_404(Class, class_id)
    body = request.get_json() or {}
    student_id = body.get("student_id")
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    student = db.get_or_404(Student, student_id)
    existing = ClassEnrollment.query.filter_by(
        student_id=student.id, class_id=cls.id
    ).first()
    if existing:
        return jsonify({"error": "Student already enrolled"}), 409

    enrollment = ClassEnrollment(student_id=student.id, class_id=cls.id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrolled", "student_id": student.id, "class_id": cls.id}), 201
