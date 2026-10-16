from sqlmodel import Session, select
from ulid import ULID
from src.app.bases.app_database import AppDatabase
from src.v1.api.setting.databases.models.setting_model import Setting

DEFAULT_SETTINGS = [
    ("APP_NAME", "Codebase"),
    ("COLOR_PRIMARY", "#2563eb"),
    ("COLOR_SECONDARY", "#84cc16"),
    ("COLOR_TERTIARY", "#1e3a8a"),
    ("DEFAULT_LOCALE", "id"),
]

class SettingSeeder:
    """
    SettingSeeder
    """

    @staticmethod
    def run () -> None:
        """
        Returns:
            None
        """
        session = Session (AppDatabase.databasePostgresql ())
        try:
            for key, value in DEFAULT_SETTINGS:
                existing = session.exec (
                    select (Setting).where (Setting.key == key, Setting.deleted_at == None)
                ).first ()
                if existing is None:
                    session.add (Setting (
                        id=str (ULID ()),
                        key=key,
                        value=value,
                        value_kind="text",
                    ))
            session.commit ()
        except Exception:
            session.rollback ()
            raise
        finally:
            session.close ()
