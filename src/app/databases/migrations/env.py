from logging.config import fileConfig
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import sys
from src.app.bases.app_database import AppDatabase
from src.app.configs.database_config import DatabaseConfig
from src.v1.api.notification.databases.models.notification_model import Notification
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.databases.models.password_reset_token_model import PasswordResetToken

sys.path.insert (0, str (Path (__file__).parent.parent.parent.parent.parent))

config = context.config
fileConfig (config.config_file_name)

target_metadata = AppDatabase.databasePostgresqlMetadata ()

databaseConfig = DatabaseConfig.config ()
config.set_main_option ("sqlalchemy.url", databaseConfig.postgre_uri ())

def run_migrations_offline () -> None:
    """
    Returns:
        None
    """
    url = config.get_main_option ("sqlalchemy.url")
    context.configure (
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction ():
        context.run_migrations ()

def run_migrations_online () -> None:
    """
    Returns:
        None
    """
    connectable = engine_from_config (
        config.get_section (config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect () as connection:
        context.configure (
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction ():
            context.run_migrations ()

if context.is_offline_mode ():
    run_migrations_offline ()
else:
    run_migrations_online ()
