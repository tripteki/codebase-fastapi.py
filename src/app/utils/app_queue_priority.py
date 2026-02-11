from typing import Dict, Optional
from src.app.bases.app_queue import AppQueue
from rq.job import Job

def enqueue_with_priority (
    base_queue: str,
    job_name: str,
    data: Dict[str, object],
    priority: str = "normal",
    job_timeout: Optional[int] = None,
    result_ttl: Optional[int] = None,
    failure_ttl: Optional[int] = None
) -> Job:
    """
    Args:
        base_queue (str)
        job_name (str)
        data (Dict[str, object])
        priority (str)
        job_timeout (Optional[int])
        result_ttl (Optional[int])
        failure_ttl (Optional[int])
    Returns:
        Job
    """
    if priority in PRIORITY_QUEUES:
        queue_name = PRIORITY_QUEUES[priority]
    else:
        queue_name = base_queue

    return AppQueue.enqueue (
        queue_name,
        job_name,
        data,
        job_timeout=job_timeout,
        result_ttl=result_ttl,
        failure_ttl=failure_ttl
    )
