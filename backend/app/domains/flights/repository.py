from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.flights.models import Flight


class FlightRepository:
    def get_by_id(self, db: Session, flight_id: str) -> Optional[Flight]:
        stmt = select(Flight).where(Flight.id == flight_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_From(self, db: Session, From: str) -> Sequence[Flight]:
        stmt = select(Flight).where(Flight.From == From.strip().upper())
        return list(db.execute(stmt).scalars().all())

    def get_by_To(self, db: Session, To: str) -> Sequence[Flight]:
        stmt = select(Flight).where(Flight.To == To.strip().upper())
        return list(db.execute(stmt).scalars().all())

    def create(
        self,
        db: Session,
        *,
        id: str,
        From: str,
        To: str,
        aircraft: str,
        departure: str,
        arrival: str,
        duty_hrs: float,
    ) -> Flight:
        flight = Flight(
            id=id,
            From=From,
            To=To,
            aircraft=aircraft,
            departure=departure,
            arrival=arrival,
            duty_hrs=duty_hrs,
        )
        db.add(flight)
        db.commit()
        db.refresh(flight)
        return flight

    def list(
        self,
        db: Session,
        *,
        From: Optional[str] = None,
        To: Optional[str] = None,
        date: Optional[str] = None,
        aircraft: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Flight]:
        stmt = select(Flight)

        if From:
            stmt = stmt.where(Flight.From == From.strip().upper())

        if To:
            stmt = stmt.where(Flight.To == To.strip().upper())

        if date:
            # Filter by departure date (contains the date string)
            stmt = stmt.where(Flight.departure.contains(date.strip()))

        if aircraft:
            stmt = stmt.where(Flight.aircraft.ilike(f"%{aircraft.strip()}%"))

        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())
