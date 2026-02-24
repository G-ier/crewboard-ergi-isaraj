from typing import Generator, Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    user: str = "nonroot"
    password: str = "crewy11"
    host: str = "db"
    port: int = 5432
    name: str = "crewboard"


DB_SETTINGS = DBSettings()
DB_URL = URL.create(
    "postgresql+psycopg",
    username=DB_SETTINGS.user,
    password=DB_SETTINGS.password,
    host=DB_SETTINGS.host,
    database=DB_SETTINGS.name,
)
DB_ENGINE = create_engine(DB_URL)
DBSessionMaker = sessionmaker(DB_ENGINE)


def get_db_session() -> Generator[Session, None, None]:
    with DBSessionMaker() as db_session:
        yield db_session


DBSession = Annotated[Session, Depends(get_db_session)]