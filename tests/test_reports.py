"""
Tests for Reports API endpoints.
"""
from datetime import date, timedelta
from tests.conftest import make_student


def _yesterday():
    return (date.today() - timedelta(days=1)).isoformat()


def _days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def setup_student_with_attendance(client, num_records=5):
    """Create one student with multiple attendance records and return the student data."""
    stu = make_student(client).get_json()["data"]
    statuses = ["Present", "Present", "Present", "Absent", "Late"]
    for i, status in enumerate(statuses[:num_records]):
        dt = _days_ago(i + 1)
        client.post("/api/attendance", json={
            "student_id": stu["id"],
            "date": dt,
            "status": status,
        })
    return stu


class TestAttendanceReport:
    def test_report_returns_all_records(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/attendance")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["total"] >= 5

    def test_report_filter_by_status(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/attendance?status=Present")
        assert res.status_code == 200
        records = res.get_json()["data"]
        assert all(r["status"] == "Present" for r in records)

    def test_report_filter_by_date_range(self, client):
        setup_student_with_attendance(client, num_records=5)
        date_from = _days_ago(3)
        date_to   = _days_ago(1)
        res = client.get(f"/api/reports/attendance?date_from={date_from}&date_to={date_to}")
        assert res.status_code == 200
        records = res.get_json()["data"]
        # All records should be within the date range
        for r in records:
            assert date_from <= r["date"] <= date_to

    def test_report_invalid_date_format(self, client):
        res = client.get("/api/reports/attendance?date_from=not-a-date")
        assert res.status_code == 400

    def test_report_filter_by_department(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/attendance?department=Computer+Science")
        assert res.status_code == 200

    def test_report_csv_format(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/attendance?format=csv")
        assert res.status_code == 200
        assert "text/csv" in res.content_type


class TestAttendanceSummary:
    def test_summary_returns_per_student_data(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/summary")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["total"] >= 1

    def test_summary_attendance_percentage(self, client):
        """3 Present + 1 Late + 1 Absent = 4/5 = 80%."""
        setup_student_with_attendance(client, num_records=5)
        res = client.get("/api/reports/summary")
        assert res.status_code == 200
        summary = res.get_json()["data"]
        assert len(summary) == 1
        s = summary[0]
        assert s["total"] == 5
        assert s["present"] == 3
        assert s["absent"] == 1
        assert s["late"] == 1
        # attendance_percentage = (present + late) / total * 100 = 4/5 * 100 = 80%
        assert s["attendance_percentage"] == 80.0

    def test_summary_filter_by_department(self, client):
        setup_student_with_attendance(client)
        res = client.get("/api/reports/summary?department=Computer+Science")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True


class TestDashboardStats:
    def test_dashboard_returns_stats(self, client):
        res = client.get("/api/reports/dashboard")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        keys = {"total_students", "total_employees", "present_today", "absent_today", "attendance_percentage"}
        assert keys.issubset(data["data"].keys())

    def test_dashboard_counts_students(self, client):
        make_student(client)
        res = client.get("/api/reports/dashboard")
        assert res.get_json()["data"]["total_students"] == 1
