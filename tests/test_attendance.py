"""
Tests for Attendance API endpoints.
"""
from datetime import date, timedelta
from tests.conftest import make_student


def _today():
    return date.today().isoformat()


def _yesterday():
    return (date.today() - timedelta(days=1)).isoformat()


def make_attendance(client, student_id, overrides=None):
    """POST an attendance record and return the response."""
    data = {
        "student_id": student_id,
        "date": _yesterday(),
        "status": "Present",
    }
    if overrides:
        data.update(overrides)
    return client.post("/api/attendance", json=data)


class TestCreateAttendance:
    def test_create_attendance_success(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        res = make_attendance(client, student_pk)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "Present"

    def test_create_attendance_invalid_status(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        res = make_attendance(client, student_pk, overrides={"status": "BadStatus"})
        assert res.status_code == 400

    def test_create_attendance_missing_student(self, client):
        res = make_attendance(client, 99999)
        assert res.status_code == 404

    def test_create_attendance_future_date(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        future = (date.today() + timedelta(days=1)).isoformat()
        res = make_attendance(client, student_pk, overrides={"date": future})
        assert res.status_code == 400

    def test_create_attendance_all_statuses(self, client):
        """Each valid status should be accepted."""
        for i, status in enumerate(["Present", "Absent", "Late", "Leave"]):
            stu = make_student(client, overrides={
                "student_id": f"STU-{i}", "email": f"s{i}@test.edu"
            }).get_json()["data"]["id"]
            res = make_attendance(client, stu, overrides={"status": status})
            assert res.status_code == 201, f"Failed for status: {status}"


class TestDuplicateAttendancePrevention:
    def test_duplicate_same_date_rejected(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        make_attendance(client, student_pk)
        # Second attempt for same student + same date
        res = make_attendance(client, student_pk)
        assert res.status_code == 409
        assert "already exists" in res.get_json()["message"]

    def test_different_dates_allowed(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        make_attendance(client, student_pk, overrides={"date": _yesterday()})
        # A different date should succeed
        two_days_ago = (date.today() - timedelta(days=2)).isoformat()
        res = make_attendance(client, student_pk, overrides={"date": two_days_ago})
        assert res.status_code == 201


class TestUpdateAttendance:
    def test_update_attendance_status(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        att_id = make_attendance(client, student_pk).get_json()["data"]["id"]
        res = client.put(f"/api/attendance/{att_id}", json={"status": "Absent"})
        assert res.status_code == 200
        assert res.get_json()["data"]["status"] == "Absent"

    def test_update_attendance_with_remarks(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        att_id = make_attendance(client, student_pk).get_json()["data"]["id"]
        res = client.put(f"/api/attendance/{att_id}", json={"remarks": "Medical leave"})
        assert res.status_code == 200
        assert res.get_json()["data"]["remarks"] == "Medical leave"

    def test_update_attendance_not_found(self, client):
        res = client.put("/api/attendance/99999", json={"status": "Absent"})
        assert res.status_code == 404

    def test_update_attendance_invalid_status(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        att_id = make_attendance(client, student_pk).get_json()["data"]["id"]
        res = client.put(f"/api/attendance/{att_id}", json={"status": "Invalid"})
        assert res.status_code == 400


class TestDeleteAttendance:
    def test_delete_attendance_success(self, client):
        student_pk = make_student(client).get_json()["data"]["id"]
        att_id = make_attendance(client, student_pk).get_json()["data"]["id"]
        res = client.delete(f"/api/attendance/{att_id}")
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_delete_attendance_not_found(self, client):
        res = client.delete("/api/attendance/99999")
        assert res.status_code == 404

    def test_delete_removes_record(self, client):
        """After deletion, the record should not appear in list."""
        student_pk = make_student(client).get_json()["data"]["id"]
        att_id = make_attendance(client, student_pk).get_json()["data"]["id"]
        client.delete(f"/api/attendance/{att_id}")
        res = client.get("/api/attendance")
        ids = [r["id"] for r in res.get_json()["data"]]
        assert att_id not in ids
