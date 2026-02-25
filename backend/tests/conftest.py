import os

os.environ.setdefault("database_user", "nonroot")
os.environ.setdefault("database_password", "crewy11")
os.environ.setdefault("database_host", "db")
os.environ.setdefault("database_port", "5432")
os.environ.setdefault("database_name", "crewboard")

import pytest
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker, Session


TEST_DB_URL = URL.create(
    "postgresql+psycopg",
    username=os.environ.get("database_user"),
    password=os.environ.get("database_password"),
    host=os.environ.get("database_host"),
    database=os.environ.get("database_name"),
    port=int(os.environ.get("database_port")),
)

test_engine = create_engine(TEST_DB_URL)
TestSessionMaker = sessionmaker(test_engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    session = TestSessionMaker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function", autouse=True)
def setup_test_data(db_session: Session):
    db_session.execute(text("DELETE FROM crew_assignments"))
    db_session.execute(text("DELETE FROM flights"))
    db_session.execute(text("DELETE FROM crew_members"))
    db_session.commit()

    db_session.execute(text("""
        INSERT INTO crew_members (id, name, email, qualifications, base) VALUES
        ('E0001', 'Alice Meyer', 'alice.meyer@example.com', 'A320', 'FRA'),
        ('E0002', 'Bob Khan', 'bob.khan@example.com', 'A320', 'FRA'),
        ('E0003', 'Carla Silva', 'carla.silva@example.com', 'B737', 'LIS'),
        ('E0004', 'Dan Novak', 'dan.novak@example.com', 'A320,B737', 'FRA'),
        ('E0005', 'Eve Ionescu', 'eve.ionescu@example.com', 'E190', 'FRA')
    """))

    db_session.execute(text("""
        INSERT INTO flights (id, "From", "To", aircraft, departure, arrival, "Duty_hrs") VALUES
        ('FQ001', 'FRA', 'LIS', 'A320', '2026-03-01T08:00:00Z', '2026-03-01T10:00:00Z', 2.0),
        ('FR010', 'LIS', 'FRA', 'A320', '2026-03-03T06:00:00Z', '2026-03-03T10:00:00Z', 4.0),
        ('FR011', 'FRA', 'CDG', 'A320', '2026-03-03T19:59:00Z', '2026-03-03T21:59:00Z', 2.0),
        ('FR012', 'FRA', 'CDG', 'A320', '2026-03-03T20:00:00Z', '2026-03-03T22:00:00Z', 2.0),
        ('FD020', 'FRA', 'MAD', 'A320', '2026-03-04T00:30:00Z', '2026-03-04T04:30:00Z', 4.0),
        ('FD021', 'MAD', 'FRA', 'A320', '2026-03-04T05:30:00Z', '2026-03-04T09:30:00Z', 4.0),
        ('FD022', 'FRA', 'AMS', 'A320', '2026-03-04T12:00:00Z', '2026-03-04T14:00:00Z', 2.0),
        ('FO030', 'FRA', 'BCN', 'A320', '2026-03-02T10:00:00Z', '2026-03-02T14:00:00Z', 4.0),
        ('FO031', 'FRA', 'MXP', 'A320', '2026-03-02T13:00:00Z', '2026-03-02T16:00:00Z', 3.0),
        ('AA200', 'FRA', 'LHR', 'A320', '2026-03-05T06:00:00Z', '2026-03-05T10:00:00Z', 4.0),
        ('AA201', 'FRA', 'ATH', 'A320', '2026-03-05T12:00:00Z', '2026-03-05T16:00:00Z', 4.0),
        ('AA203', 'FRA', 'IST', 'A320', '2026-03-05T18:00:00Z', '2026-03-05T22:00:00Z', 4.0),
        ('AA202', 'LIS', 'FRA', 'B737', '2026-03-05T07:00:00Z', '2026-03-05T11:00:00Z', 4.0),
        ('AA204', 'FRA', 'JFK', 'A350', '2026-03-05T09:00:00Z', '2026-03-05T17:00:00Z', 8.0)
    """))

    db_session.execute(text("""
        INSERT INTO crew_assignments (flight_id, crew_employee_id, created_at) VALUES
        ('FR010', 'E0001', '2026-02-25T09:00:00Z'),
        ('FD020', 'E0002', '2026-02-25T09:10:00Z'),
        ('FD021', 'E0002', '2026-02-25T09:11:00Z'),
        ('FO030', 'E0004', '2026-02-25T09:20:00Z')
    """))
    
    db_session.commit()
    
    yield
    
    db_session.execute(text("DELETE FROM crew_assignments"))
    db_session.execute(text("DELETE FROM flights"))
    db_session.execute(text("DELETE FROM crew_members"))
    db_session.commit()
