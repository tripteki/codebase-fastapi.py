from typing import Generator
from fastapi import Depends
from sqlmodel import Session
from src.app.bases.app_database import AppDatabase

def get_db () -> Generator[Session, None, None]:
    """
    Returns:
        Generator[Session, None, None]
    """
    engine = AppDatabase.databasePostgresql ()
    with Session (engine) as session:
        yield session
