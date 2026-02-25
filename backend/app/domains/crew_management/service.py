from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domains.crew_management.repository import CrewRepository
from app.domains.crew_management.schemas import CrewCreate, CrewUpdate
from app.domains.crew_management.models import CrewMember


class CrewService:
    def __init__(self) -> None:
        self.repo = CrewRepository()

    def create_crew(self, db: Session, payload: CrewCreate) -> CrewMember:

        if self.repo.get_by_id(db, payload.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="id already exists",
            )
        if self.repo.get_by_email(db, str(payload.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email already exists",
            )

        return self.repo.create(
            db,
            id=payload.id,
            name=payload.name,
            email=str(payload.email),
            base_airport=payload.base_airport,
            qualification_codes=payload.qualifications,
        )

    def get_crew(self, db: Session, crew_id: str) -> CrewMember:
        crew = self.repo.get_by_id(db, crew_id)
        if not crew:
            raise HTTPException(status_code=404, detail="crew member does not exist")
        return crew

    def update_crew(self, db: Session, crew_id: str, payload: CrewUpdate) -> CrewMember:
        crew = self.get_crew(db, crew_id)

        if payload.email is not None:
            existing = self.repo.get_by_email(db, str(payload.email))
            if existing and existing.id != crew.id:
                raise HTTPException(status_code=409, detail="email already exists")

        return self.repo.update(
            db,
            crew,
            name=payload.name,
            email=str(payload.email) if payload.email is not None else None,
            base_airport=payload.base_airport,
            qualification_codes=payload.qualifications,
        )

    def list_crew(
        self,
        db: Session,
        *,
        base_airport: str | None,
        qualified_for: str | None,
        limit: int,
        offset: int,
    ):
        return self.repo.list(
            db,
            base_airport=base_airport,
            qualified_for=qualified_for,
            limit=limit,
            offset=offset,
        )