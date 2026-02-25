from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.models import AppBase


class Flight(AppBase):
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    From: Mapped[str] = mapped_column(String(10))
    To: Mapped[str] = mapped_column(String(10))
    aircraft: Mapped[str] = mapped_column(String(20))
    departure: Mapped[str] = mapped_column(String(50))
    arrival: Mapped[str] = mapped_column(String(50))
    duty_hrs: Mapped[float] = mapped_column("Duty_hrs", Float, primary_key=False)

    # Relationship to CrewAssignment - using string reference to avoid circular import
    # The actual relationship configuration happens after all models are imported
    assignments = relationship(
        "CrewAssignment",
        back_populates="flight",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
