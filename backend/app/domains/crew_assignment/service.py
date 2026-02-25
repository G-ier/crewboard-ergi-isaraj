from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from app.domains.crew_assignment.models import CrewAssignment
from app.domains.crew_assignment.repository import CrewAssignmentRepository
from app.domains.crew_assignment.schemas import (
    AssignmentCreate,
    AssignmentValidationResult,
    ValidationError,
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
            quals = [q.strip().upper() for q in crew.qualifications.split(",")]
            aircraft_type = flight.aircraft.strip().upper()
            
            has_qualification = any(
                aircraft_type in q or q in aircraft_type 
                for q in quals
            )
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
        
        # departure #TODO parse date
        new_departure = self._parse_flight_time(new_flight.departure)
        if not new_departure:
            return None

        # try to get the last assginment period
        stmt = (
            select(CrewAssignment)
            .join(Flight, CrewAssignment.flight_id == Flight.id)
            .where(
                and_(
                    CrewAssignment.crew_employee_id == crew_employee_id,
                    CrewAssignment.removed_at.is_(None),
                )
            )
            .order_by(Flight.arrival.desc())
            .limit(1)
        )
        last_assignment = db.execute(stmt).scalar_one_or_none()

        # if found then check with last flight if new_dep - arrival_time is less than allowed
        if last_assignment:
            last_flight = db.execute(
                select(Flight).where(Flight.id == last_assignment.flight_id)
            ).scalar_one_or_none()
            
            if last_flight:
                last_arrival = self._parse_flight_time(last_flight.arrival)
                if last_arrival and new_departure:
                    
                    rest_hours = (new_departure - last_arrival).total_seconds() / 3600
                    if rest_hours < 10:
                        return ValidationError(
                            code="INSUFFICIENT_REST",
                            message=f"Rest period of {rest_hours:.1f} hours is less than required 10 hours. "
                                    f"Last flight arrived at {last_flight.arrival}, new flight departs at {new_flight.departure}",
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

        # all assignments for 1 day
        start_of_day = datetime.combine(flight_date, datetime.min.time())
        end_of_day = datetime.combine(flight_date, datetime.max.time())

        stmt = (
            select(CrewAssignment)
            .join(Flight, CrewAssignment.flight_id == Flight.id)
            .where(
                and_(
                    CrewAssignment.crew_employee_id == crew_employee_id,
                    CrewAssignment.removed_at.is_(None),
                    Flight.departure.contains(flight_date.strftime("%b %d")),
                )
            )
        )
        existing_assignments = db.execute(stmt).scalars().all()

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
        """Check if the crew member would have overlapping flights."""
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
        
        try:
            
            current_year = datetime.now().year
            parsed = datetime.strptime(f"{current_year}, {time_str}", "%Y, %b %d, %H:%M")
            return parsed
        except ValueError:
            try:
                
                current_year = datetime.now().year
                parsed = datetime.strptime(f"{current_year}, {time_str}", "%Y, %b %d, %H:%M")
                return parsed
            except ValueError:
                return None

    def create_assignment(
        self, db: Session, payload: AssignmentCreate
    ) -> tuple[Optional[CrewAssignment], AssignmentValidationResult]:
    
        validation = self.validate_assignment(
            db, payload.flight_id, payload.crew_employee_id
        )

        if not validation.valid:
            return None, validation

    
        assignment = self.repo.create(
            db,
            flight_id=payload.flight_id,
            crew_employee_id=payload.crew_employee_id,
        )

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
