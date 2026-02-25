"""
Pytest configuration for unit tests using real database data.
"""
import os
import pytest
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session

# Set environment variables for database connection
os.environ.setdefault("database_user", "nonroot")
os.environ.setdefault("database_password", "crewy11")
os.environ.setdefault("database_host", "db")
os.environ.setdefault("database_port", "5432")
os.environ.setdefault("database_name", "crewboard")


# Create database URL for testing
TEST_DB_URL = URL.create(
    "postgresql+psycopg",
    username="nonroot",
    password="crewy11",
    host="db",
    database="crewboard",
)

# Create engine and session maker
test_engine = create_engine(TEST_DB_URL)
TestSessionMaker = sessionmaker(test_engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provide a database session for tests.
    Each test gets a fresh session.
    """
    session = TestSessionMaker()
    try:
        yield session
    finally:
        session.close()
