from typing import Any, Annotated, Generator, Optional
from fastapi import Depends
from sqlalchemy import text
from sqlmodel import create_engine, Session, SQLModel
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse
from src.app.configs.database_config import DatabaseConfig

class AppDatabase:
    """
    AppDatabase

    Attributes:
        _database_postgresql (None)
        _database_mongonosql (None)
        database_mongonosql_session (None)
        database_postgresql_session (Depends (databasePostgresqlSession))
    """
    _database_postgresql = None
    _database_mongonosql: Optional[AsyncIOMotorClient] = None

    @classmethod
    def databasePostgresqlMetadata (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Any
        """
        return SQLModel.metadata

    @classmethod
    def databasePostgresqlSession (cls) -> Generator[Session, None, None]:
        """
        Args:
            cls
        Returns:
            Generator[Session, None, None]
        """
        with Session (
            cls.databasePostgresql ()
        ) as session:

            yield session

    @classmethod
    async def databasePostgresqlInit (cls, app) -> Any:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            Any
        """
        with cls.databasePostgresql ().connect () as connection:
            connection.execute (text ("SELECT 1"))
        return cls.database_postgresql_session

    @classmethod
    def databasePostgresql (cls) -> Any:
        """
        Args:
            cls
        Returns:
            Engine
        """
        if cls._database_postgresql is None:
            databaseConfig = DatabaseConfig.config ()
            cls._database_postgresql = create_engine (databaseConfig.postgre_uri (), echo=True)
        return cls._database_postgresql

    @classmethod
    def databaseMongonosqlDatabase (cls, databaseName: Optional[str] = None) -> Any:
        """
        Args:
            cls
            databaseName (Optional[str])
        Returns:
            Any (AsyncIOMotorDatabase)
        """
        client = cls.databaseMongonosql ()
        if databaseName:
            return client[databaseName]
        if cls.database_mongonosql_session is None:
            databaseConfig = DatabaseConfig.config ()
            uri = databaseConfig.mongo_uri ()
            parsed = urlparse (uri)
            db_name = parsed.path.lstrip ('/') if parsed.path else "test"
            cls.database_mongonosql_session = client[db_name]
        return cls.database_mongonosql_session

    @classmethod
    async def databaseMongonosqlClose (cls) -> None:
        """
        Args:
            cls
        Returns:
            None
        """
        if cls._database_mongonosql:
            cls._database_mongonosql.close ()
            cls._database_mongonosql = None
            cls.database_mongonosql_session = None

    @classmethod
    def databaseMongonosql (cls) -> AsyncIOMotorClient:
        """
        Args:
            cls
        Returns:
            AsyncIOMotorClient
        """
        if cls._database_mongonosql is None:
            databaseConfig = DatabaseConfig.config ()
            cls._database_mongonosql = AsyncIOMotorClient (databaseConfig.mongo_uri ())
        return cls._database_mongonosql

    database_postgresql_session: Annotated[Session, Depends (databasePostgresqlSession)] = Depends (databasePostgresqlSession)
    database_mongonosql_session: Optional[Any] = None
