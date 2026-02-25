from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domains.flights.repository import FlightRepository
from app.domains.flights.schemas import (
    FlightCreate, ScheduleItem, CrewScheduleResponse, FlightRead
)
from app.domains.flights.models import Flight
from app.domains.crew_management.models import CrewMember
from sqlalchemy import select


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

    def _parse_flight_time(self, time_str: str) -> Optional[datetime]:
        
        try:
            current_year = datetime.now().year
            parsed = datetime.strptime(f"{current_year}, {time_str}", "%Y, %b %d, %H:%M")
            return parsed
        except ValueError:
            return None

    def get_crew_schedule(self, db: Session, crew_member_id: str) -> CrewScheduleResponse:

        crew = db.execute(
            select(CrewMember).where(CrewMember.id == crew_member_id)
        ).scalar_one_or_none()
        
        if not crew:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crew member {crew_member_id} not found",
            )

        flights = self.repo.get_flights_by_crew_member(db, crew_member_id)
        
        schedule: list[ScheduleItem] = []
        
        for i, flight in enumerate(flights):
            schedule.append(ScheduleItem(
                type="flight",
                flight=FlightRead.model_validate(flight),
            ))
            
            if i < len(flights) - 1:
                next_flight = flights[i + 1]
                current_arrival = self._parse_flight_time(flight.arrival)
                next_departure = self._parse_flight_time(next_flight.departure)
                
                if current_arrival and next_departure:
                    rest_hours = (next_departure - current_arrival).total_seconds() / 3600
                    date_str = next_flight.departure.split(",")[0].strip()
                    
                    schedule.append(ScheduleItem(
                        type="rest",
                        rest_hours=round(rest_hours, 1),
                        date=date_str,
                    ))

        return CrewScheduleResponse(
            crew_member_id=crew_member_id,
            schedule=schedule,
        )
