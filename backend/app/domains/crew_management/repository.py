from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.crew_management.models import CrewMember


class CrewRepository:
    def get_by_id(self, db: Session, crew_id: int) -> Optional[CrewMember]:
        stmt = select(CrewMember).where(CrewMember.id == crew_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, db: Session, email: str) -> Optional[CrewMember]:
        stmt = select(CrewMember).where(CrewMember.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_qualification(self, db: Session, code: str) -> Optional[CrewMember]:
        stmt = select(CrewMember).where(code.in_(CrewMember.qualifications))
        return db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        db: Session,
        *,
        id: str,
        name: str,
        email: str,
        base_airport: str,
        qualification_codes: list[str],
    ) -> CrewMember:
        crew = CrewMember(
            id=id,
            name=name,
            email=email,
            base=base_airport,
        )
        db.add(crew)
        db.flush()  # assigns crew.id

        if qualification_codes is not None:
            quals = ", ".join(map(str, qualification_codes))
            crew.qualifications = quals

        db.commit()
        db.refresh(crew)
        return crew

    def update(
        self,
        db: Session,
        crew: CrewMember,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        base_airport: Optional[str] = None,
        qualification_codes: Optional[list[str]] = None, 
    ) -> CrewMember:
        if name is not None:
            crew.name = name
        if email is not None:
            crew.email = email
        if base_airport is not None:
            crew.base = base_airport

        if qualification_codes is not None:
            quals = [self.get_or_create_qualification(db, code) for code in qualification_codes]
            crew.qualifications = quals

        db.commit()
        db.refresh(crew)
        return crew

    def list(
        self,
        db: Session,
        *,
        base_airport: Optional[str] = None,
        qualified_for: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CrewMember]:
        stmt = select(CrewMember)

        if base_airport:
            stmt = stmt.where(CrewMember.base == base_airport.strip().upper())

        if qualified_for:
            q = qualified_for.strip().upper()
            stmt = stmt.where(CrewMember.qualifications.contains(q))

        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())