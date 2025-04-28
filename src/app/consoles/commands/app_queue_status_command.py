from typing import Optional
import click
from src.app.bases.app_console import Command
from src.app.bases.app_queue import AppQueue
from src.app.constants.queue_constants import ALL_QUEUES
from rq import Queue

@Command (name="queue:status", help="Check queue and job status")
@click.argument ("job_id", required=False)
@click.option ("--queue", type=str, default=None, help="Queue name to check")
def queueStatusCommand (job_id: Optional[str], queue: Optional[str]) -> None:
    """
    Args:
        job_id (Optional[str])
        queue (Optional[str])
    Returns:
        None
    """
    if job_id:
        status = AppQueue.getJobStatus (job_id)
        if status:
            click.echo (f"Job {job_id} status: {status}")

            job = AppQueue.getJob (job_id)
            if job:
                click.echo (f"  Created at: {job.created_at}")
                if job.started_at:
                    click.echo (f"  Started at: {job.started_at}")
                if job.ended_at:
                    click.echo (f"  Ended at: {job.ended_at}")
                if job.exc_info:
                    click.echo (f"  Error: {job.exc_info}")
        else:
            click.echo (f"Job {job_id} not found")
    elif queue:
        queue_obj = AppQueue.getQueue (queue)
        click.echo (f"Queue: {queue}")
        click.echo (f"  Jobs in queue: {len (queue_obj)}")
        click.echo (f"  Failed jobs: {len (queue_obj.failed_job_registry)}")
    else:
        click.echo ("Queue Status:")
        click.echo ("=" * 50)
        for queue_name in ALL_QUEUES:
            queue_obj = AppQueue.getQueue (queue_name)
            click.echo (f"\n{queue_name}:")
            click.echo (f"  Jobs in queue: {len (queue_obj)}")
            click.echo (f"  Failed jobs: {len (queue_obj.failed_job_registry)}")
