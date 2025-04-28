from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from typing import Any, Annotated, Generator
from src.app.configs.database_config import DatabaseConfig

class AppDatabase:
    """
    AppDatabase
    """
    @classmethod
    def databaseEngine (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Engine
        """
        if cls._engine is None:
            databaseConfig = DatabaseConfig.config ()
            cls._engine = create_engine (databaseConfig.postgre_uri, echo=True)
        return cls._engine

    @classmethod
    def databaseSession (cls) -> Generator[Session, None, None]:
        """
        Args:
            cls
        Returns:
            Generator[Session, None, None]
        """
        with Session (
            cls.databaseEngine ()
        ) as session:
            yield session

    @classmethod
    async def database (cls, app) -> Any:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Any
        """
        with cls.databaseEngine ().connect () as connection:
            connection.execute (text ("SELECT 1"))
        SQLModel.metadata.create_all (
            cls.databaseEngine ()
        )
        return cls.sql

    """
    Attributes:
        _engine (None)
        sql (Depends (databaseSession))
    """
    _engine = None
    sql: Annotated[Session, Depends (databaseSession)] = Depends (databaseSession)
