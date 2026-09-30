"""
Tests for Student CRUD API endpoints.
"""
import json
from tests.conftest import make_student


class TestCreateStudent:
    def test_create_student_success(self, client):
        res = make_student(client)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["student_id"] == "STU-T1"

    def test_create_student_missing_field(self, client):
        res = client.post("/api/students", json={"name": "No Email"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False

    def test_create_student_invalid_email(self, client):
        res = make_student(client, overrides={"email": "not-an-email"})
        assert res.status_code == 400

    def test_create_student_duplicate_id(self, client):
        make_student(client)
        res = make_student(client)           # same student_id
        assert res.status_code == 409
        assert "already exists" in res.get_json()["message"]

    def test_create_student_duplicate_email(self, client):
        make_student(client)
        res = make_student(client, overrides={"student_id": "STU-T2"})   # different id, same email
        assert res.status_code == 409

    def test_create_student_invalid_semester(self, client):
        res = make_student(client, overrides={"semester": 99})
        assert res.status_code == 400


class TestReadStudent:
    def test_list_students_empty(self, client):
        res = client.get("/api/students")
        assert res.status_code == 200
        assert res.get_json()["data"] == []

    def test_list_students(self, client):
        make_student(client)
        res = client.get("/api/students")
        assert res.status_code == 200
        assert res.get_json()["total"] == 1

    def test_get_student_by_id(self, client):
        created = make_student(client).get_json()["data"]["id"]
        res = client.get(f"/api/students/{created}")
        assert res.status_code == 200
        assert res.get_json()["data"]["id"] == created

    def test_get_student_not_found(self, client):
        res = client.get("/api/students/99999")
        assert res.status_code == 404

    def test_search_students(self, client):
        make_student(client)
        res = client.get("/api/students?search=STU-T1")
        assert res.status_code == 200
        assert res.get_json()["total"] == 1

    def test_search_students_no_match(self, client):
        make_student(client)
        res = client.get("/api/students?search=DOESNOTEXIST")
        assert res.status_code == 200
        assert res.get_json()["total"] == 0


class TestUpdateStudent:
    def test_update_student_success(self, client):
        created_id = make_student(client).get_json()["data"]["id"]
        res = client.put(f"/api/students/{created_id}", json={"name": "Updated Name"})
        assert res.status_code == 200
        assert res.get_json()["data"]["name"] == "Updated Name"

    def test_update_student_not_found(self, client):
        res = client.put("/api/students/99999", json={"name": "Ghost"})
        assert res.status_code == 404

    def test_update_student_duplicate_id(self, client):
        id1 = make_student(client).get_json()["data"]["id"]
        make_student(client, overrides={"student_id": "STU-T2", "email": "other@test.edu"})
        res = client.put(f"/api/students/{id1}", json={"student_id": "STU-T2"})
        assert res.status_code == 409


class TestDeleteStudent:
    def test_delete_student_success(self, client):
        created_id = make_student(client).get_json()["data"]["id"]
        res = client.delete(f"/api/students/{created_id}")
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_delete_student_not_found(self, client):
        res = client.delete("/api/students/99999")
        assert res.status_code == 404
