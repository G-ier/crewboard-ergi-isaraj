from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.engine import get_db_session
from app.domains.crew_management.schemas import CrewCreate, CrewRead, CrewUpdate
from app.domains.crew_management.service import CrewService

router = APIRouter(prefix="/crew", tags=["Crew Management"])
service = CrewService()

@router.get("/{crew_id}", response_model=CrewRead)
def get_crew(crew_id: str, db: Session = Depends(get_db_session)):
    crew = service.get_crew(db, crew_id)
    return CrewRead(
        id=crew.id,
        name=crew.name,
        email=crew.email,
        base_airport=crew.base,
        qualifications=crew.qualifications.split(",") if crew.qualifications else [],
    )

@router.post("", response_model=CrewRead, status_code=201)
def create_crew(payload: CrewCreate, db: Session = Depends(get_db_session)):
    crew = service.create_crew(db, payload)
    return CrewRead(
        id=crew.id,
        name=crew.name,
        email=crew.email,
        base_airport=crew.base,
        qualifications=crew.qualifications.split(",") if crew.qualifications else [],
    )

@router.patch("/{crew_id}", response_model=CrewRead)
def update_crew(crew_id: str, payload: CrewUpdate, db: Session = Depends(get_db_session)):
    crew = service.update_crew(db, crew_id, payload)
    return CrewRead(
        id=crew.id,
        name=crew.name,
        email=crew.email,
        base_airport=crew.base,
        qualifications=crew.qualifications.split(",") if crew.qualifications else [],
    )


@router.get("", response_model=list[CrewRead])
def list_crew(
    base_airport: str | None = Query(default=None),
    qualified_for: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
):
    rows = service.list_crew(
        db,
        base_airport=base_airport,
        qualified_for=qualified_for,
        limit=limit,
        offset=offset,
    )
    return [
        CrewRead(
            id=c.id,
            name=c.name,
            email=c.email,
            base_airport=c.base,
            qualifications=c.qualifications.split(",") if c.qualifications else [],
        )
        for c in rows
    ]