from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.v1.api.setting.databases.models.setting_model import Setting

SETTINGS_DIRECTORY = Path ("storage/disks/public/settings")

class SettingRepository:
    """
    SettingRepository
    """

    @staticmethod
    def getSession () -> Session:
        """
        Returns:
            Session
        """
        return Session (AppDatabase.databasePostgresql ())

    async def all (self) -> List[Setting]:
        """
        Args:
            self
        Returns:
            List[Setting]
        """
        session = self.getSession ()
        try:
            return list (
                session.exec (
                    select (Setting)
                    .where (Setting.deleted_at == None)
                    .order_by (Setting.key.asc ())
                ).all ()
            )
        finally:
            session.close ()

    async def findById (self, id: str) -> Optional[Setting]:
        """
        Args:
            id (str)
        Returns:
            Optional[Setting]
        """
        session = self.getSession ()
        try:
            return session.exec (
                select (Setting).where (Setting.id == id, Setting.deleted_at == None)
            ).first ()
        finally:
            session.close ()

    async def findByKey (self, key: str) -> Optional[Setting]:
        """
        Args:
            key (str)
        Returns:
            Optional[Setting]
        """
        session = self.getSession ()
        try:
            return session.exec (
                select (Setting).where (Setting.key == key, Setting.deleted_at == None)
            ).first ()
        finally:
            session.close ()

    async def upsert (
        self,
        *,
        id: Optional[str],
        key: str,
        value: Optional[str],
        valueKind: str,
    ) -> Setting:
        """
        Args:
            id (Optional[str])
            key (str)
            value (Optional[str])
            valueKind (str)
        Returns:
            Setting
        """
        session = self.getSession ()
        try:
            setting = None
            if id:
                setting = session.exec (
                    select (Setting).where (Setting.id == id, Setting.deleted_at == None)
                ).first ()

            if setting is None:
                setting = session.exec (
                    select (Setting).where (Setting.key == key)
                ).first ()
            else:
                stale = session.exec (
                    select (Setting).where (
                        Setting.key == key,
                        Setting.id != setting.id,
                        Setting.deleted_at != None,
                    )
                ).first ()
                if stale is not None:
                    session.delete (stale)
                    session.flush ()

            if setting is None:
                setting = Setting (
                    id=str (ULID ()),
                    key=key,
                    value=value,
                    value_kind=valueKind,
                )
            else:
                setting.key = key
                setting.value = value
                setting.value_kind = valueKind
                setting.deleted_at = None
                setting.updated_at = datetime.utcnow ()

            session.add (setting)
            session.commit ()
            session.refresh (setting)
            return setting
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    async def softDelete (self, id: str) -> None:
        """
        Args:
            id (str)
        Returns:
            None
        """
        session = self.getSession ()
        try:
            setting = session.exec (
                select (Setting).where (Setting.id == id, Setting.deleted_at == None)
            ).first ()
            if setting is None:
                return
            setting.deleted_at = datetime.utcnow ()
            setting.updated_at = datetime.utcnow ()
            session.add (setting)
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()

    @staticmethod
    async def saveFile (content: bytes, extension: str) -> str:
        """
        Args:
            content (bytes)
            extension (str)
        Returns:
            str
        """
        SETTINGS_DIRECTORY.mkdir (parents=True, exist_ok=True)
        filename = f"{uuid4 ().hex}{extension}"
        destination = SETTINGS_DIRECTORY / filename
        destination.write_bytes (content)
        return f"settings/{filename}"
