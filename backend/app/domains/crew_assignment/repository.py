from datetime import datetime
from typing import Optional, Sequence
from datetime import timedelta

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.domains.crew_assignment.models import CrewAssignment


class CrewAssignmentRepository:
    def get_by_id(self, db: Session, assignment_id: int) -> Optional[CrewAssignment]:
        stmt = select(CrewAssignment).where(CrewAssignment.id == assignment_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_flight_and_crew(
        self, db: Session, flight_id: str, crew_employee_id: str
    ) -> Optional[CrewAssignment]:
        stmt = select(CrewAssignment).where(
            and_(
                CrewAssignment.flight_id == flight_id,
                CrewAssignment.crew_employee_id == crew_employee_id,
                CrewAssignment.removed_at.is_(None),
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_flight(self, db: Session, flight_id: str) -> Sequence[CrewAssignment]:
        stmt = select(CrewAssignment).where(
            and_(
                CrewAssignment.flight_id == flight_id,
                CrewAssignment.removed_at.is_(None),
            )
        )
        return list(db.execute(stmt).scalars().all())

    def get_by_crew_member(
        self, db: Session, crew_employee_id: str
    ) -> Sequence[CrewAssignment]:
        stmt = select(CrewAssignment).where(
            and_(
                CrewAssignment.crew_employee_id == crew_employee_id,
                CrewAssignment.removed_at.is_(None),
            )
        )
        return list(db.execute(stmt).scalars().all())

    def create(
        self,
        db: Session,
        *,
        flight_id: str,
        crew_employee_id: str,
    ) -> CrewAssignment:
        assignment = CrewAssignment(
            flight_id=flight_id,
            crew_employee_id=crew_employee_id,
            created_at=datetime.utcnow(),
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def soft_delete(self, db: Session, assignment: CrewAssignment) -> CrewAssignment:
        assignment.removed_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
        return assignment

    def list(
        self,
        db: Session,
        *,
        flight_id: Optional[str] = None,
        crew_employee_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CrewAssignment]:
        stmt = select(CrewAssignment)

        if flight_id:
            stmt = stmt.where(CrewAssignment.flight_id == flight_id)

        if crew_employee_id:
            stmt = stmt.where(CrewAssignment.crew_employee_id == crew_employee_id)

        if not include_removed:
            stmt = stmt.where(CrewAssignment.removed_at.is_(None))

        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_active_assignments_for_crew_on_date(
        self, db: Session, crew_employee_id: str, date: datetime
    ) -> Sequence[CrewAssignment]:

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

        stmt = select(CrewAssignment).where(
            and_(
                CrewAssignment.crew_employee_id == crew_employee_id,
                CrewAssignment.removed_at.is_(None),
                CrewAssignment.created_at >= start_of_day,
                CrewAssignment.created_at <= end_of_day,
            )
        )
        return list(db.execute(stmt).scalars().all())

    def get_conflicting_assignments(
        self, db: Session, crew_employee_id: str, flight_id: str
    ) -> Sequence[CrewAssignment]:
        
        # for now, just return assignments for the same crew member
        stmt = select(CrewAssignment).where(
            and_(
                CrewAssignment.crew_employee_id == crew_employee_id,
                CrewAssignment.removed_at.is_(None),
                CrewAssignment.flight_id != flight_id,
            )
        )
        return list(db.execute(stmt).scalars().all())
