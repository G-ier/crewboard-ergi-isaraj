"""Shared SQLAlchemy base class for all domain models."""
from sqlalchemy.orm import DeclarativeBase


class AppBase(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
