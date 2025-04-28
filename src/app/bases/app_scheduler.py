from typing import Callable, Optional, Dict, List, Union
from datetime import datetime
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

class AppScheduler:
    """
    AppScheduler

    Attributes:
        _scheduler (Optional[AsyncIOScheduler])
        _started (bool)
    """
    _scheduler: Optional[AsyncIOScheduler] = None
    _started: bool = False

    @classmethod
    def scheduler (cls) -> AsyncIOScheduler:
        """
        Args:
            cls
        Returns:
            AsyncIOScheduler
        """
        if cls._scheduler is None:
            cls._scheduler = AsyncIOScheduler ()
        return cls._scheduler

    @classmethod
    def start (cls) -> None:
        """
        Args:
            cls
        Returns:
            None
        """
        if not cls._started:
            scheduler = cls.scheduler ()
            scheduler.start ()
            cls._started = True

    @classmethod
    def shutdown (cls) -> None:
        """
        Args:
            cls
        Returns:
            None
        """
        if cls._scheduler and cls._started:
            cls._scheduler.shutdown ()
            cls._started = False

    @classmethod
    def addCronJob (
        cls,
        func: Callable[..., object],
        cronExpression: str,
        id: Optional[str] = None,
        args: Optional[tuple[object, ...]] = None,
        kwargs: Optional[Dict[str, object]] = None,
        replaceExisting: bool = True
    ) -> Job:
        """
        Args:
            func (Callable[..., object])
            cronExpression (str)
            id (Optional[str])
            args (Optional[tuple[object, ...]])
            kwargs (Optional[Dict[str, object]])
            replaceExisting (bool)
        Returns:
            Job
        """
        scheduler = cls.scheduler ()
        trigger = CronTrigger.from_crontab (cronExpression)
        return scheduler.add_job (
            func,
            trigger=trigger,
            id=id,
            args=args or (),
            kwargs=kwargs or {},
            replace_existing=replaceExisting
        )

    @classmethod
    def addIntervalJob (
        cls,
        func: Callable[..., object],
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
        days: Optional[int] = None,
        weeks: Optional[int] = None,
        id: Optional[str] = None,
        args: Optional[tuple[object, ...]] = None,
        kwargs: Optional[Dict[str, object]] = None,
        replaceExisting: bool = True
    ) -> Job:
        """
        Args:
            func (Callable[..., object])
            seconds (Optional[int])
            minutes (Optional[int])
            hours (Optional[int])
            days (Optional[int])
            weeks (Optional[int])
            id (Optional[str])
            args (Optional[tuple[object, ...]])
            kwargs (Optional[Dict[str, object]])
            replaceExisting (bool)
        Returns:
            Job
        """
        scheduler = cls.scheduler ()
        trigger = IntervalTrigger (
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks
        )
        return scheduler.add_job (
            func,
            trigger=trigger,
            id=id,
            args=args or (),
            kwargs=kwargs or {},
            replace_existing=replaceExisting
        )

    @classmethod
    def addDateJob (
        cls,
        func: Callable[..., object],
        runDate: Union[datetime, str],
        id: Optional[str] = None,
        args: Optional[tuple[object, ...]] = None,
        kwargs: Optional[Dict[str, object]] = None,
        replaceExisting: bool = True
    ) -> Job:
        """
        Args:
            func (Callable[..., object])
            runDate (Union[datetime, str])
            id (Optional[str])
            args (Optional[tuple[object, ...]])
            kwargs (Optional[Dict[str, object]])
            replaceExisting (bool)
        Returns:
            Job
        """
        scheduler = cls.scheduler ()
        trigger = DateTrigger (run_date=runDate)
        return scheduler.add_job (
            func,
            trigger=trigger,
            id=id,
            args=args or (),
            kwargs=kwargs or {},
            replace_existing=replaceExisting
        )

    @classmethod
    def removeJob (cls, jobId: str) -> None:
        """
        Args:
            jobId (str)
        Returns:
            None
        """
        if cls._scheduler:
            cls._scheduler.remove_job (jobId)

    @classmethod
    def getJob (cls, jobId: str) -> Optional[Job]:
        """
        Args:
            jobId (str)
        Returns:
            Optional[Job]
        """
        if cls._scheduler:
            return cls._scheduler.get_job (jobId)
        return None

    @classmethod
    def getJobs (cls) -> List[Job]:
        """
        Args:
            cls
        Returns:
            List[Job]
        """
        if cls._scheduler:
            return cls._scheduler.get_jobs ()
        return []

def Cron (cronExpression: str, id: Optional[str] = None) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Args:
        cronExpression (str)
        id (Optional[str])
    Returns:
        Callable[[Callable[..., object]], Callable[..., object]]
    """
    def decorator (func: Callable[..., object]) -> Callable[..., object]:
        """
        Args:
            func (Callable[..., object])
        Returns:
            Callable[..., object]
        """
        AppScheduler.addCronJob (func, cronExpression, id=id or func.__name__)
        return func
    return decorator

def Interval (
    seconds: Optional[int] = None,
    minutes: Optional[int] = None,
    hours: Optional[int] = None,
    days: Optional[int] = None,
    weeks: Optional[int] = None,
    id: Optional[str] = None
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Args:
        seconds (Optional[int])
        minutes (Optional[int])
        hours (Optional[int])
        days (Optional[int])
        weeks (Optional[int])
        id (Optional[str])
    Returns:
        Callable[[Callable[..., object]], Callable[..., object]]
    """
    def decorator (func: Callable[..., object]) -> Callable[..., object]:
        """
        Args:
            func (Callable[..., object])
        Returns:
            Callable[..., object]
        """
        AppScheduler.addIntervalJob (
            func,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
            id=id or func.__name__
        )

        return func
    return decorator
