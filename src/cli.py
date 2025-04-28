from pathlib import Path
import sys

sys.path.insert (0, str (Path (__file__).parent.parent))

from src.app.bases.app_console import AppConsole
from src.app.consoles.commands.app_cache_command import cacheClearCommand
from src.app.consoles.commands.app_migrate_command import migrateUpCommand, migrateDownCommand, migrateStatusCommand
from src.app.consoles.commands.app_queue_command import queueWorkCommand
from src.app.consoles.commands.app_queue_failed_command import queueFailedCommand
from src.app.consoles.commands.app_queue_status_command import queueStatusCommand
from src.app.consoles.commands.app_secret_command import secretCommand
from src.v1.api.user.consoles.commands.user_seed_command import userSeedCommand

if __name__ == "__main__":
    AppConsole.run ()
