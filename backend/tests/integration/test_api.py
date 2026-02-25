import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAssignmentsAPI:
    def test_create_assignment_success(self, db_session):
        response = client.post("/assignments", json={"flight_id": "FQ001", "crew_employee_id": "E0001"})
        assert response.status_code == 201
        data = response.json()
        assert data["flight_id"] == "FQ001"
        assert data["crew_employee_id"] == "E0001"

    def test_create_assignment_qualification_violation(self, db_session):
        response = client.post("/assignments", json={"flight_id": "FQ001", "crew_employee_id": "E0003"})
        assert response.status_code == 400

    def test_create_assignment_rest_violation(self, db_session):
        response = client.post("/assignments", json={"flight_id": "FR011", "crew_employee_id": "E0001"})
        assert response.status_code == 400

    def test_create_assignment_duty_limit_violation(self, db_session):
        response = client.post("/assignments", json={"flight_id": "FD022", "crew_employee_id": "E0002"})
        assert response.status_code == 400

    def test_create_assignment_overlap_violation(self, db_session):
        response = client.post("/assignments", json={"flight_id": "FO031", "crew_employee_id": "E0004"})
        assert response.status_code == 400

    def test_list_assignments(self, db_session):
        response = client.get("/assignments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAutoAssign:
    def test_auto_assign_success(self, db_session):
        response = client.post("/assignments/auto")
        assert response.status_code == 200
        data = response.json()
        
        assert "assigned" in data
        assert "failed" in data
        assert data["total_flights"] == 14
        assert data["total_assigned"] >= 4
        
        failed_ids = [f["flight_id"] for f in data["failed"]]
        assert "AA204" in failed_ids
        
        for assignment in data["assigned"]:
            assert "flight_id" in assignment
            assert "crew_member_id" in assignment
