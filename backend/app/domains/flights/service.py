from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domains.flights.repository import FlightRepository
from app.domains.flights.schemas import FlightCreate
from app.domains.flights.models import Flight


class FlightService:
    def __init__(self) -> None:
        self.repo = FlightRepository()

    def create_flight(self, db: Session, payload: FlightCreate) -> Flight:
        existing = self.repo.get_by_id(db, payload.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="flight id already exists",
            )

        return self.repo.create(
            db,
            id=payload.id,
            From=payload.From,
            To=payload.To,
            aircraft=payload.aircraft,
            departure=payload.departure,
            arrival=payload.arrival,
            duty_hrs=payload.duty_hrs,
        )

    def get_flight(self, db: Session, flight_id: str) -> Flight:
        flight = self.repo.get_by_id(db, flight_id)
        if not flight:
            raise HTTPException(status_code=404, detail="flight does not exist")
        return flight

    def list_flights(
        self,
        db: Session,
        *,
        From: str | None,
        To: str | None,
        date: str | None,
        aircraft: str | None,
        limit: int,
        offset: int,
    ):
        return self.repo.list(
            db,
            From=From,
            To=To,
            date=date,
            aircraft=aircraft,
            limit=limit,
            offset=offset,
        )
