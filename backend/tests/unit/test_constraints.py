import pytest
from app.domains.crew_assignment.service import CrewAssignmentService


class TestQualificationConstraint:
    def test_qualification_valid(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FQ001", "E0001")
        assert result.valid is True

    def test_qualification_violation(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FQ001", "E0003")
        assert result.valid is False
        codes = [e.code for e in result.errors]
        assert "QUALIFICATION_MISMATCH" in codes


class TestRestPeriodConstraint:
    def test_rest_period_violation(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FR011", "E0001")
        assert result.valid is False
        codes = [e.code for e in result.errors]
        assert "INSUFFICIENT_REST" in codes

    def test_rest_period_exactly_10h_passes(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FR012", "E0001")
        assert result.valid is True


class TestDailyDutyLimitConstraint:
    def test_daily_duty_violation(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FD022", "E0002")
        assert result.valid is False
        codes = [e.code for e in result.errors]
        assert "DAILY_DUTY_EXCEEDED" in codes


class TestOverlapConstraint:
    def test_overlap_violation(self, db_session):
        service = CrewAssignmentService()
        result = service.validate_assignment(db_session, "FO031", "E0004")
        assert result.valid is False
        codes = [e.code for e in result.errors]
        assert "FLIGHT_OVERLAP" in codes
