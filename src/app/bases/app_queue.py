from typing import Dict, Optional, Callable
from typing_extensions import Self
import redis
from rq import Queue
from rq.job import Job
from src.app.configs.app_config import AppConfig
from src.app.configs.queue_config import QueueConfig

class AppQueue:
    """
    AppQueue

    Attributes:
        _queues (Dict[str, Queue])
        _connection (Optional[redis.Redis])
    """
    _queues: Dict[str, Queue] = {}
    _connection: Optional[redis.Redis] = None

    DEFAULT_JOB_TIMEOUT = 3600
    DEFAULT_RESULT_TTL = 86400
    DEFAULT_FAILURE_TTL = 604800

    @classmethod
    def connection (cls) -> redis.Redis:
        """
        Args:
            cls
        Returns:
            redis.Redis
        """
        if cls._connection is None:
            queueConfig = QueueConfig.config ()
            redisUri = queueConfig.redis_uri ()
            cls._connection = redis.from_url (redisUri, decode_responses=False)
        return cls._connection

    @classmethod
    def getQueue (cls, queueName: str) -> Queue:
        """
        Args:
            queueName (str)
        Returns:
            Queue
        """
        if queueName not in cls._queues:
            cls._queues[queueName] = Queue (queueName, connection=cls.connection ())
        return cls._queues[queueName]

    @classmethod
    def enqueue (
        cls,
        queueName: str,
        jobName: str,
        *args: object,
        job_timeout: Optional[int] = None,
        result_ttl: Optional[int] = None,
        failure_ttl: Optional[int] = None,
        **kwargs: object
    ) -> Job:
        """
        Args:
            queueName (str)
            jobName (str)
            *args (object)
            job_timeout (Optional[int])
            result_ttl (Optional[int])
            failure_ttl (Optional[int])
            **kwargs (object)
        Returns:
            Job
        """
        queue = cls.getQueue (queueName)
        from src.app.bases.app_queue_processor import AppQueueProcessor
        handler = AppQueueProcessor.getHandler (queueName, jobName)
        if handler:
            timeout = job_timeout if job_timeout is not None else cls.DEFAULT_JOB_TIMEOUT
            rttl = result_ttl if result_ttl is not None else cls.DEFAULT_RESULT_TTL
            fttl = failure_ttl if failure_ttl is not None else cls.DEFAULT_FAILURE_TTL

            return queue.enqueue (
                handler,
                *args,
                job_timeout=timeout,
                result_ttl=rttl,
                failure_ttl=fttl,
                **kwargs
            )
        raise ValueError (f"No handler found for queue '{queueName}' and job '{jobName}'")

    @classmethod
    def getJob (cls, jobId: str) -> Optional[Job]:
        """
        Args:
            cls
            jobId (str)
        Returns:
            Optional[Job]
        """
        try:
            return Job.fetch (jobId, connection=cls.connection ())
        except Exception:
            return None

    @classmethod
    def getJobStatus (cls, jobId: str) -> Optional[str]:
        """
        Args:
            cls
            jobId (str)
        Returns:
            Optional[str]
        """
        job = cls.getJob (jobId)
        if job:
            return job.get_status ()
        return None

    @classmethod
    def queue (cls, queueName: str = "default") -> Self:
        """
        Args:
            queueName (str)
        Returns:
            AppQueue
        """
        return cls

def Processor (queueName: str) -> Callable[[type], type]:
    """
    Args:
        queueName (str)
    Returns:
        Callable[[type], type]
    """
    def decorator (cls) -> type:
        """
        Returns:
            type
        """
        cls._queue_name = queueName
        return cls
    return decorator

def Process (jobName: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Args:
        jobName (str)
    Returns:
        Callable[[Callable[..., object]], Callable[..., object]]
    """
    def decorator (handler: Callable[..., object]) -> Callable[..., object]:
        """
        Args:
            handler (Callable[..., object])
        Returns:
            Callable[..., object]
        """
        handler._job_name = jobName
        return handler
    return decorator
