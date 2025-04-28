import logging
from src.app.bases.app_scheduler import AppScheduler, Cron
from src.app.configs.app_config import AppConfig

logger = logging.getLogger (__name__)

class UserScheduleService:
    """
    UserScheduleService
    """

    @staticmethod
    @Cron ("* * * * *", id="clean")
    async def handleClean () -> None:
        """
        Returns:
            None
        """
        logger.info ("Cleaning...")

        try:
            logger.info ("Cleaned!")

        except Exception as error:
            logger.error (f"Uncleaned: {error}")
