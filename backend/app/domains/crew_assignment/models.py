from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.models import AppBase

# Use this to avoid circular imports at runtime
if TYPE_CHECKING:
    from app.domains.flights.models import Flight
    from app.domains.crew_management.models import CrewMember


class CrewAssignment(AppBase):
    __tablename__ = "crew_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_id: Mapped[str] = mapped_column(ForeignKey("flights.id", ondelete="CASCADE"))
    crew_employee_id: Mapped[str] = mapped_column(ForeignKey("crew_members.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    removed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    # Relationships - using string references to avoid circular imports
    flight: Mapped["Flight"] = relationship("Flight", back_populates="assignments")
    crew_member: Mapped["CrewMember"] = relationship("CrewMember", back_populates="assignments")

    def __repr__(self) -> str:
        return f"<CrewAssignment(id={self.id}, flight_id={self.flight_id}, crew_employee_id={self.crew_employee_id})>"
