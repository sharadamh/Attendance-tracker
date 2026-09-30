"""
Tests for Employee CRUD API endpoints.
"""
from tests.conftest import make_employee


class TestCreateEmployee:
    def test_create_employee_success(self, client):
        res = make_employee(client)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["employee_id"] == "EMP-T1"

    def test_create_employee_missing_field(self, client):
        res = client.post("/api/employees", json={"name": "No Email"})
        assert res.status_code == 400
        assert res.get_json()["success"] is False

    def test_create_employee_invalid_email(self, client):
        res = make_employee(client, overrides={"email": "bad-email"})
        assert res.status_code == 400

    def test_create_employee_duplicate_id(self, client):
        make_employee(client)
        res = make_employee(client)       # same employee_id
        assert res.status_code == 409

    def test_create_employee_duplicate_email(self, client):
        make_employee(client)
        res = make_employee(client, overrides={"employee_id": "EMP-T2"})   # same email
        assert res.status_code == 409


class TestReadEmployee:
    def test_list_employees_empty(self, client):
        res = client.get("/api/employees")
        assert res.status_code == 200
        assert res.get_json()["data"] == []

    def test_list_employees(self, client):
        make_employee(client)
        res = client.get("/api/employees")
        assert res.status_code == 200
        assert res.get_json()["total"] == 1

    def test_get_employee_by_id(self, client):
        emp_id = make_employee(client).get_json()["data"]["id"]
        res = client.get(f"/api/employees/{emp_id}")
        assert res.status_code == 200

    def test_get_employee_not_found(self, client):
        res = client.get("/api/employees/99999")
        assert res.status_code == 404

    def test_search_employees(self, client):
        make_employee(client)
        res = client.get("/api/employees?search=EMP-T1")
        assert res.status_code == 200
        assert res.get_json()["total"] == 1


class TestUpdateEmployee:
    def test_update_employee_success(self, client):
        emp_id = make_employee(client).get_json()["data"]["id"]
        res = client.put(f"/api/employees/{emp_id}", json={"designation": "Professor"})
        assert res.status_code == 200
        assert res.get_json()["data"]["designation"] == "Professor"

    def test_update_employee_not_found(self, client):
        res = client.put("/api/employees/99999", json={"name": "Ghost"})
        assert res.status_code == 404


class TestDeleteEmployee:
    def test_delete_employee_success(self, client):
        emp_id = make_employee(client).get_json()["data"]["id"]
        res = client.delete(f"/api/employees/{emp_id}")
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_delete_employee_not_found(self, client):
        res = client.delete("/api/employees/99999")
        assert res.status_code == 404
