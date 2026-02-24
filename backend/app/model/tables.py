from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AppBase(DeclarativeBase):
    pass


class CrewMembers(AppBase):
    __tablename__ = "crew_members"

    employee_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    qualifications: Mapped[str | None]
    base: Mapped[str | None]


class Flights(AppBase):
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(primary_key=True)
    from_airport: Mapped[str]
    to_airport: Mapped[str]
    aircraft: Mapped[str]
    departure: Mapped[str]
    arrival: Mapped[str]
    duty_hrs: Mapped[float]
