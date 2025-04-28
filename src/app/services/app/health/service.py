from enum import Enum
from typing import Dict, Optional
import psutil
from sqlalchemy import text
from src.app.bases.app_context import AppContext
from src.app.bases.app_database import AppDatabase
from src.app.configs.app_config import AppConfig

class HealthStatus (str, Enum):
    """
    HealthStatus (str, Enum)

    Attributes:
        UP (str)
        DOWN (str)
    """
    UP = "up"
    DOWN = "down"

class HealthCheckResult:
    """
    HealthCheckResult

    Attributes:
        status (HealthStatus)
        info (Optional[Dict[str, object]])
    """
    def __init__ (self, status: HealthStatus, info: Optional[Dict[str, object]] = None) -> None:
        """
        Args:
            status (HealthStatus)
            info (Optional[Dict[str, object]])
        Returns:
            None
        """
        self.status = status
        self.info = info or {}

class AppHealthService:
    """
    AppHealthService
    """
    @staticmethod
    def checkMemoryHeap (threshold: int) -> HealthCheckResult:
        """
        Args:
            threshold (int)
        Returns:
            HealthCheckResult
        """
        try:
            process = psutil.Process ()
            memory_info = process.memory_info ()
            heap_used = memory_info.rss

            is_healthy = heap_used < threshold

            return HealthCheckResult (
                status=HealthStatus.UP if is_healthy else HealthStatus.DOWN,
                info={
                    "memory_allocation": {
                        "status": HealthStatus.UP.value if is_healthy else HealthStatus.DOWN.value,
                        "heap_used": heap_used,
                        "heap_used_mb": round (heap_used / (1024 * 1024), 2),
                        "threshold": threshold,
                        "threshold_mb": round (threshold / (1024 * 1024), 2),
                    }
                }
            )
        except Exception as e:
            return HealthCheckResult (
                status=HealthStatus.DOWN,
                info={
                    "memory_allocation": {
                        "status": HealthStatus.DOWN.value,
                        "error": str (e),
                    }
                }
            )

    @staticmethod
    def checkMemoryRss (threshold: int) -> HealthCheckResult:
        """
        Args:
            threshold (int)
        Returns:
            HealthCheckResult
        """
        try:
            process = psutil.Process ()
            memory_info = process.memory_info ()
            rss_used = memory_info.rss

            is_healthy = rss_used < threshold

            return HealthCheckResult (
                status=HealthStatus.UP if is_healthy else HealthStatus.DOWN,
                info={
                    "memory_total": {
                        "status": HealthStatus.UP.value if is_healthy else HealthStatus.DOWN.value,
                        "rss_used": rss_used,
                        "rss_used_mb": round (rss_used / (1024 * 1024), 2),
                        "threshold": threshold,
                        "threshold_mb": round (threshold / (1024 * 1024), 2),
                    }
                }
            )
        except Exception as e:
            return HealthCheckResult (
                status=HealthStatus.DOWN,
                info={
                    "memory_total": {
                        "status": HealthStatus.DOWN.value,
                        "error": str (e),
                    }
                }
            )

    @staticmethod
    async def checkDatabase () -> HealthCheckResult:
        """
        Args:
            None
        Returns:
            HealthCheckResult
        """
        try:
            engine = AppDatabase.databasePostgresql ()

            if engine is None:
                return HealthCheckResult (
                    status=HealthStatus.DOWN,
                    info={
                        "database": {
                            "status": HealthStatus.DOWN.value,
                            "error": "Database not initialized",
                        }
                    }
                )

            with engine.connect () as connection:
                connection.execute (text ("SELECT 1"))

            return HealthCheckResult (
                status=HealthStatus.UP,
                info={
                    "database": {
                        "status": HealthStatus.UP.value,
                    }
                }
            )
        except Exception as e:
            return HealthCheckResult (
                status=HealthStatus.DOWN,
                info={
                    "database": {
                        "status": HealthStatus.DOWN.value,
                        "error": str (e),
                    }
                }
            )

    @staticmethod
    async def checkCache () -> HealthCheckResult:
        """
        Args:
            None
        Returns:
            HealthCheckResult
        """
        try:
            cache = AppContext.cacheRedis ()

            if cache is None:
                return HealthCheckResult (
                    status=HealthStatus.DOWN,
                    info={
                        "cache": {
                            "status": HealthStatus.DOWN.value,
                            "error": "Cache not initialized",
                        }
                    }
                )

            await cache.ping ()

            return HealthCheckResult (
                status=HealthStatus.UP,
                info={
                    "cache": {
                        "status": HealthStatus.UP.value,
                    }
                }
            )
        except Exception as e:
            return HealthCheckResult (
                status=HealthStatus.DOWN,
                info={
                    "cache": {
                        "status": HealthStatus.DOWN.value,
                        "error": str (e),
                    }
                }
            )

    @classmethod
    async def checkAll (cls, memory_threshold: Optional[int] = None) -> Dict[str, object]:
        """
        Args:
            memory_threshold (Optional[int])
        Returns:
            Dict[str, object]
        """
        app_config = AppConfig.config ()
        is_production = app_config.app_env == "production"

        if memory_threshold is None:
            memory_threshold = 150 * 1024 * 1024 if is_production else 500 * 1024 * 1024

        heap_check = cls.checkMemoryHeap (memory_threshold)
        rss_check = cls.checkMemoryRss (memory_threshold)
        db_check = await cls.checkDatabase ()
        cache_check = await cls.checkCache ()

        all_info = {}
        all_info.update (heap_check.info)
        all_info.update (rss_check.info)
        all_info.update (db_check.info)
        all_info.update (cache_check.info)

        all_statuses = [
            heap_check.status,
            rss_check.status,
            db_check.status,
            cache_check.status,
        ]

        overall_status = HealthStatus.UP if all (s == HealthStatus.UP for s in all_statuses) else HealthStatus.DOWN

        return {
            "status": overall_status.value,
            "info": all_info,
        }
