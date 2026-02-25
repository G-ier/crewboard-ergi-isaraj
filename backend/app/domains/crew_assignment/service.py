from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.domains.crew_assignment.models import CrewAssignment
from app.domains.crew_assignment.repository import CrewAssignmentRepository
from app.domains.crew_assignment.schemas import (
    AssignmentCreate,
    AssignmentValidationResult,
    ValidationError,
    AutoAssignmentResult,
    AutoAssignmentSuccess,
    AutoAssignmentFailure,
)
from app.domains.flights.models import Flight
from app.domains.crew_management.models import CrewMember


class CrewAssignmentService:
    def __init__(self) -> None:
        self.repo = CrewAssignmentRepository()

    # SEARCHWORD validation core logic, bad request case is here
    def validate_assignment(
        self, db: Session, flight_id: str, crew_employee_id: str
    ) -> AssignmentValidationResult:
        
        errors: list[ValidationError] = []
        warnings: list[str] = []

        # crew check
        crew = db.execute(
            select(CrewMember).where(CrewMember.id == crew_employee_id)
        ).scalar_one_or_none()
        if not crew:
            errors.append(
                ValidationError(
                    code="CREW_NOT_FOUND",
                    message=f"Crew member {crew_employee_id} does not exist",
                )
            )
            return AssignmentValidationResult(valid=False, errors=errors)

        # flight existssss
        flight = db.execute(
            select(Flight).where(Flight.id == flight_id)
        ).scalar_one_or_none()
        if not flight:
            errors.append(
                ValidationError(
                    code="FLIGHT_NOT_FOUND",
                    message=f"Flight {flight_id} does not exist",
                )
            )
            return AssignmentValidationResult(valid=False, errors=errors)

        # aircraft check
        if crew.qualifications:
            quals = [q.strip() for q in crew.qualifications.split(",")]
            aircraft_type = flight.aircraft.strip()
            
            has_qualification = aircraft_type in quals
            
            if not has_qualification:
                errors.append(
                    ValidationError(
                        code="QUALIFICATION_MISMATCH",
                        message=f"Crew member does not hold required qualification for {flight.aircraft}. "
                                f"Required: {flight.aircraft}, Has: {crew.qualifications}",
                    )
                )
        else:
            errors.append(
                ValidationError(
                    code="NO_QUALIFICATIONS",
                    message=f"Crew member has no qualifications recorded",
                )
            )

        # deduplication
        existing = self.repo.get_by_flight_and_crew(db, flight_id, crew_employee_id)
        if existing:
            errors.append(
                ValidationError(
                    code="DUPLICATE_ASSIGNMENT",
                    message=f"Crew member is already assigned to this flight",
                )
            )
            return AssignmentValidationResult(valid=False, errors=errors)

        # rest check
        rest_violation = self._check_rest_period(db, crew_employee_id, flight)
        if rest_violation:
            errors.append(rest_violation)

        # limit on work check
        duty_limit_violation = self._check_daily_duty_limit(db, crew_employee_id, flight)
        if duty_limit_violation:
            errors.append(duty_limit_violation)

        # overlap check
        overlap_violation = self._check_no_overlap(db, crew_employee_id, flight)
        if overlap_violation:
            errors.append(overlap_violation)

        return AssignmentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_rest_period(
        self, db: Session, crew_employee_id: str, new_flight: Flight
    ) -> Optional[ValidationError]:
        
        new_departure = self._parse_flight_time(new_flight.departure)
        if not new_departure:
            return None

        new_arrival = self._parse_flight_time(new_flight.arrival)
        if not new_arrival:
            return None

        assignments = self.repo.get_by_crew_member(db, crew_employee_id)
        
        for assignment in assignments:
            flight = db.execute(
                select(Flight).where(Flight.id == assignment.flight_id)
            ).scalar_one_or_none()
            
            if flight:
                last_arrival = self._parse_flight_time(flight.arrival)
                if last_arrival and new_departure:
                    if last_arrival < new_departure:
                        rest_hours = (new_departure - last_arrival).total_seconds() / 3600
                        if rest_hours < 10:
                            return ValidationError(
                                code="INSUFFICIENT_REST",
                                message=f"Rest period of {rest_hours:.1f} hours is less than required 10 hours. "
                                        f"Last flight arrived at {flight.arrival}, new flight departs at {new_flight.departure}",
                            )

        return None

    # check for date of selected flight if duty_hrs for total flights in that date is more than 8
    def _check_daily_duty_limit(
        self, db: Session, crew_employee_id: str, new_flight: Flight
    ) -> Optional[ValidationError]:
        
        new_departure = self._parse_flight_time(new_flight.departure)
        if not new_departure:
            return None

        flight_date = new_departure.date()

        all_assignments = self.repo.get_by_crew_member(db, crew_employee_id)
        
        existing_assignments = []
        for assignment in all_assignments:
            flight = db.execute(
                select(Flight).where(Flight.id == assignment.flight_id)
            ).scalar_one_or_none()
            if flight:
                dep = self._parse_flight_time(flight.departure)
                if dep and dep.date() == flight_date:
                    existing_assignments.append(assignment)

        # get total
        total_hours = new_flight.duty_hrs
        for assignment in existing_assignments:
            flight = db.execute(
                select(Flight).where(Flight.id == assignment.flight_id)
            ).scalar_one_or_none()
            if flight:
                total_hours += flight.duty_hrs

        if total_hours > 8:
            return ValidationError(
                code="DAILY_DUTY_EXCEEDED",
                message=f"Adding this flight would exceed the 8-hour daily duty limit. "
                        f"Total would be {total_hours:.1f} hours on {flight_date}",
            )

        return None

    def _check_no_overlap(
        self, db: Session, crew_employee_id: str, new_flight: Flight
    ) -> Optional[ValidationError]:

        new_departure = self._parse_flight_time(new_flight.departure)
        new_arrival = self._parse_flight_time(new_flight.arrival)
        
        if not new_departure or not new_arrival:
            return None

        assignments = self.repo.get_by_crew_member(db, crew_employee_id)

        for assignment in assignments:
            flight = db.execute(
                select(Flight).where(Flight.id == assignment.flight_id)
            ).scalar_one_or_none()
            
            if flight:
                existing_departure = self._parse_flight_time(flight.departure)
                existing_arrival = self._parse_flight_time(flight.arrival)
                
                if existing_departure and existing_arrival:
                    
                    if (new_departure < existing_arrival and new_arrival > existing_departure):
                        return ValidationError(
                            code="FLIGHT_OVERLAP",
                            message=f"Crew member is already assigned to flight {flight.id} "
                                    f"({flight.departure} - {flight.arrival}) which overlaps with "
                                    f"the new flight ({new_flight.departure} - {new_flight.arrival})",
                        )

        return None

    def _parse_flight_time(self, time_str: str) -> Optional[datetime]:
        
        if not time_str:
            return None
            
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        try:
            current_year = datetime.now().year
            return datetime.strptime(f"{current_year}, {time_str}", "%Y, %b %d, %H:%M")
        except ValueError:
            return None

    def create_assignment(
        self, db: Session, payload: AssignmentCreate
    ) -> tuple[Optional[CrewAssignment], AssignmentValidationResult]:
    
        validation = self.validate_assignment(
            db, payload.flight_id, payload.crew_employee_id
        )

        if not validation.valid:
            
            existing = self.repo.get_any_by_flight_and_crew(
                db, payload.flight_id, payload.crew_employee_id
            )
            if existing and existing.removed_at:
                error_codes = [e.code for e in validation.errors]
                if error_codes == ["DUPLICATE_ASSIGNMENT"]:
                    reactivated = self.repo.reactivate(db, existing)
                    return reactivated, validation
            
            return None, validation

        try:
            assignment = self.repo.create(
                db,
                flight_id=payload.flight_id,
                crew_employee_id=payload.crew_employee_id,
            )
        except IntegrityError:
            db.rollback()
            existing = self.repo.get_any_by_flight_and_crew(
                db, payload.flight_id, payload.crew_employee_id
            )
            if existing and existing.removed_at:
                return self.repo.reactivate(db, existing), validation
            raise

        return assignment, validation

    def delete_assignment(self, db: Session, assignment_id: int) -> CrewAssignment:
        
        assignment = self.repo.get_by_id(db, assignment_id)
        if not assignment:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found",
            )
        
        if assignment.removed_at:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignment already removed",
            )

        return self.repo.soft_delete(db, assignment)

    def list_assignments(
        self,
        db: Session,
        *,
        flight_id: Optional[str] = None,
        crew_employee_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CrewAssignment]:
        
        return self.repo.list(
            db,
            flight_id=flight_id,
            crew_employee_id=crew_employee_id,
            include_removed=include_removed,
            limit=limit,
            offset=offset,
        )

    def get_assignment(self, db: Session, assignment_id: int) -> CrewAssignment:
        
        assignment = self.repo.get_by_id(db, assignment_id)
        if not assignment:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found",
            )
        return assignment

    def auto_assign(self, db: Session) -> AutoAssignmentResult:
        all_crew = db.execute(select(CrewMember)).scalars().all()
        all_flights = db.execute(select(Flight)).scalars().all()
        
        assigned_flights = set()
        crew_hours = {c.id: 0.0 for c in all_crew}
        
        assigned = []
        failed = []
        
        for flight in all_flights:
            existing = db.execute(
                select(CrewAssignment).where(
                    and_(
                        CrewAssignment.flight_id == flight.id,
                        CrewAssignment.removed_at.is_(None)
                    )
                )
            ).scalar_one_or_none()
            if existing:
                assigned_flights.add(flight.id)
                continue
            
            eligible = []
            for crew in all_crew:
                validation = self.validate_assignment(db, flight.id, crew.id)
                if validation.valid:
                    eligible.append((crew.id, crew_hours[crew.id]))
            
            if not eligible:
                failed.append(AutoAssignmentFailure(flight_id=flight.id, reason="No eligible crew"))
                continue
            
            eligible.sort(key=lambda x: x[1])
            best_crew = eligible[0][0]
            
            assignment = CrewAssignment(
                flight_id=flight.id,
                crew_employee_id=best_crew,
                created_at=datetime.utcnow(),
            )
            db.add(assignment)
            db.commit()
            
            crew_hours[best_crew] += flight.duty_hrs
            assigned_flights.add(flight.id)
            assigned.append(AutoAssignmentSuccess(flight_id=flight.id, crew_member_id=best_crew))
        
        return AutoAssignmentResult(
            assigned=assigned,
            failed=failed,
            total_flights=len(all_flights),
            total_assigned=len(assigned),
            total_failed=len(failed),
        )
