import click
import sys
from typing import Optional
from redis import Redis
from rq import Queue
from rq.registry import FailedJobRegistry
from src.app.bases.app_console import Command
from src.app.configs.queue_config import QueueConfig
from src.app.constants.queue_constants import ALL_QUEUES

@Command (name="queue:failed", help="Manage failed queue jobs")
@click.option ("--count", is_flag=True, help="Show count of failed jobs only")
@click.option ("--queue", "-q", default=None, help="Queue name (default: all queues)")
@click.option ("--retry", "-r", is_flag=True, help="Retry all failed jobs")
@click.option ("--clear", "-c", is_flag=True, help="Clear all failed jobs")
@click.option ("--job-id", "-j", default=None, help="Retry specific job by ID")
def queueFailedCommand (count: bool, queue: Optional[str], retry: bool, clear: bool, job_id: Optional[str]) -> None:
    """
    Args:
        count (bool)
        queue (Optional[str])
        retry (bool)
        clear (bool)
        job_id (Optional[str])
    Returns:
        None
    """
    try:
        queueConfig = QueueConfig.config ()
        redis_conn = Redis.from_url (queueConfig.redis_uri (), decode_responses=False)

        queues_to_process = [queue] if queue else ALL_QUEUES

        if job_id:
            if not queue:
                click.echo ("Error: --queue is required when using --job-id", err=True)
                sys.exit (1)

            _retry_specific_job (redis_conn, queue, job_id)
            return

        total_failed = 0
        total_retried = 0
        total_cleared = 0

        for queue_name in queues_to_process:
            queue_obj = Queue (queue_name, connection=redis_conn)
            failed_registry = FailedJobRegistry (queue=queue_obj)
            failed_job_ids = failed_registry.get_job_ids ()

            if not failed_job_ids:
                if not count and len (queues_to_process) == 1:
                    click.echo (f"No failed jobs in queue '{queue_name}'")
                continue

            total_failed += len (failed_job_ids)

            if count:
                click.echo (f"Queue '{queue_name}': {len (failed_job_ids)} failed job(s)")
                continue

            if retry:
                retried = _retry_failed_jobs (queue_obj, failed_registry, failed_job_ids)
                total_retried += retried
                click.echo (f"Retried {retried} failed job(s) in queue '{queue_name}'")
                continue

            if clear:
                cleared = _clear_failed_jobs (queue_obj, failed_registry, failed_job_ids)
                total_cleared += cleared
                click.echo (f"Cleared {cleared} failed job(s) in queue '{queue_name}'")
                continue

            _list_failed_jobs (queue_obj, queue_name, failed_job_ids)

        if count:
            click.echo (f"\nTotal failed jobs: {total_failed}")
        elif retry and total_retried > 0:
            click.echo (f"\nTotal retried: {total_retried} job(s)")
        elif clear and total_cleared > 0:
            click.echo (f"\nTotal cleared: {total_cleared} job(s)")
        elif total_failed == 0 and not count and not retry and not clear:
            click.echo ("No failed jobs across all queues.")

    except Exception as e:
        click.echo (f"Error: {e}", err=True)
        import traceback
        traceback.print_exc ()
        sys.exit (1)

def _list_failed_jobs (queue: Queue, queue_name: str, job_ids: list) -> None:
    """
    Args:
        queue (Queue)
        queue_name (str)
        job_ids (list)
    Returns:
        None
    """
    click.echo (f"\nFailed jobs in queue '{queue_name}': {len (job_ids)}")
    click.echo ("=" * 80)

    for idx, job_id in enumerate (job_ids, 1):
        job = queue.fetch_job (job_id)
        if job:
            click.echo (f"\n{idx}. Job ID: {job.id}")
            click.echo (f"Created: {job.created_at}")
            click.echo (f"Failed: {job.ended_at}")
            click.echo (f"Function: {job.func_name}")

            if job.exc_info:
                error_lines = job.exc_info.split ("\n")
                error_msg = error_lines[-2] if len (error_lines) > 1 else job.exc_info
                click.echo (f"Error: {error_msg}")

            click.echo (f"Args: {job.args[:2] if job.args else 'None'}...")

def _retry_failed_jobs (queue: Queue, failed_registry: FailedJobRegistry, job_ids: list) -> int:
    """
    Args:
        queue (Queue)
        failed_registry (FailedJobRegistry)
        job_ids (list)
    Returns:
        int
    """
    retried = 0
    for job_id in job_ids:
        job = queue.fetch_job (job_id)
        if job:
            try:
                failed_registry.remove (job)
                queue.enqueue_job (job)
                retried += 1
            except Exception as e:
                click.echo (f"Failed to retry job {job_id}: {e}", err=True)
    return retried

def _clear_failed_jobs (queue: Queue, failed_registry: FailedJobRegistry, job_ids: list) -> int:
    """
    Args:
        queue (Queue)
        failed_registry (FailedJobRegistry)
        job_ids (list)
    Returns:
        int
    """
    cleared = 0
    for job_id in job_ids:
        try:
            job = queue.fetch_job (job_id)
            if job:
                job.delete ()
                cleared += 1
        except Exception as e:
            click.echo (f"Failed to clear job {job_id}: {e}", err=True)
    return cleared

def _retry_specific_job (redis_conn: Redis, queue_name: str, job_id: str) -> None:
    """
    Args:
        redis_conn (Redis)
        queue_name (str)
        job_id (str)
    Returns:
        None
    """
    queue = Queue (queue_name, connection=redis_conn)
    job = queue.fetch_job (job_id)

    if not job:
        click.echo (f"Job '{job_id}' not found in queue '{queue_name}'", err=True)
        sys.exit (1)

    if job.is_failed:
        failed_registry = FailedJobRegistry (queue=queue)
        failed_registry.remove (job)
        queue.enqueue_job (job)
        click.echo (f"Job '{job_id}' has been requeued")
    else:
        click.echo (f"Job '{job_id}' is not in failed state (status: {job.get_status ()})")
