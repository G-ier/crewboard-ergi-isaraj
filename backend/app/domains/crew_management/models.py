from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.models import AppBase


class CrewMember(AppBase):
    __tablename__ = "crew_members"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    qualifications: Mapped[str | None]
    base: Mapped[str | None]

    # Relationship to CrewAssignment
    assignments = relationship(
        "CrewAssignment",
        back_populates="crew_member",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
