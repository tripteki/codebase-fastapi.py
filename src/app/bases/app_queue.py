from typing import Dict, Any, Optional, Callable
import redis
from rq import Queue
from rq.job import Job
from src.app.configs.app_config import AppConfig
from src.app.configs.queue_config import QueueConfig

class AppQueue:
    """
    AppQueue
    """
    _queues: Dict[str, Queue] = {}
    _connection: Optional[redis.Redis] = None

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
    def enqueue (cls, queueName: str, jobName: str, *args, **kwargs) -> Job:
        """
        Args:
            queueName (str)
            jobName (str)
            *args
            **kwargs
        Returns:
            Job
        """
        queue = cls.getQueue (queueName)
        from src.app.bases.app_queue_processor import AppQueueProcessor
        handler = AppQueueProcessor.getHandler (queueName, jobName)
        if handler:
            return queue.enqueue (handler, *args, **kwargs)
        raise ValueError (f"No handler found for queue '{queueName}' and job '{jobName}'")

    @classmethod
    def queue (cls, queueName: str = "default") -> 'AppQueue':
        """
        Args:
            queueName (str)
        Returns:
            AppQueue
        """
        return cls

def Processor (queueName: str):
    """
    Args:
        queueName (str)
    Returns:
        Callable
    """
    def decorator (cls: type) -> type:
        """
        Args:
            cls (type)
        Returns:
            type
        """
        cls._queue_name = queueName
        return cls
    return decorator

def Process (jobName: str):
    """
    Args:
        jobName (str)
    Returns:
        Callable
    """
    def decorator (handler: Callable) -> Callable:
        """
        Args:
            handler (Callable)
        Returns:
            Callable
        """
        handler._job_name = jobName
        return handler
    return decorator
