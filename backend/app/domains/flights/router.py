from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.engine import get_db_session
from app.domains.flights.schemas import FlightCreate, FlightRead, CrewScheduleResponse
from app.domains.flights.service import FlightService

router = APIRouter(prefix="/flights", tags=["Flight Management"])
service = FlightService()


@router.get("/schedule/{crew_member_id}", response_model=CrewScheduleResponse)
def get_crew_schedule(
    crew_member_id: str,
    db: Session = Depends(get_db_session),
):

    return service.get_crew_schedule(db, crew_member_id)


@router.get("/{flight_id}", response_model=FlightRead)
def get_flight(flight_id: str, db: Session = Depends(get_db_session)):
    flight = service.get_flight(db, flight_id)
    return FlightRead(
        id=flight.id,
        From=flight.From,
        To=flight.To,
        aircraft=flight.aircraft,
        departure=flight.departure,
        arrival=flight.arrival,
        duty_hrs=flight.duty_hrs,
    )


@router.post("", response_model=FlightRead, status_code=201)
def create_flight(payload: FlightCreate, db: Session = Depends(get_db_session)):
    flight = service.create_flight(db, payload)
    return FlightRead(
        id=flight.id,
        From=flight.From,
        To=flight.To,
        aircraft=flight.aircraft,
        departure=flight.departure,
        arrival=flight.arrival,
        duty_hrs=flight.duty_hrs,
    )


@router.get("", response_model=list[FlightRead])
def list_flights(
    From: str | None = Query(default=None),
    To: str | None = Query(default=None),
    date: str | None = Query(default=None, description="filter by DEPARTURE date"),
    aircraft: str | None = Query(default=None, description="filtering by aircraft type or number"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
):
    rows = service.list_flights(
        db,
        From=From,
        To=To,
        date=date,
        aircraft=aircraft,
        limit=limit,
        offset=offset,
    )
    return [
        FlightRead(
            id=f.id,
            From=f.From,
            To=f.To,
            aircraft=f.aircraft,
            departure=f.departure,
            arrival=f.arrival,
            duty_hrs=f.duty_hrs,
        )
        for f in rows
    ]
