from typing import Optional
import click
import sys
from src.app.bases.app_console import Command
from src.app.bases.app_event_listener import AppEventListener
from src.app.bases.app_queue_processor import AppQueueProcessor
from src.app.constants.queue_constants import ALL_QUEUES, USER_ADMIN_QUEUE, NOTIFICATION_QUEUE

@Command (name="queue:work", help="Start queue worker for processing background jobs")
@click.argument ("queues", nargs=-1)
@click.option ("--max-jobs", type=int, default=None, help="Maximum concurrent jobs per worker")
@click.option ("--worker-ttl", type=int, default=None, help="Worker TTL in seconds (default: 420)")
def queueWorkCommand (queues: tuple[str, ...], max_jobs: Optional[int], worker_ttl: Optional[int]) -> None:
    """
    Args:
        queues (tuple[str, ...])
    Returns:
        None
    """
    try:
        click.echo ("Loading event listeners...")
        AppEventListener.loadListeners (None)

        click.echo ("Loading queue processors...")
        AppQueueProcessor.loadProcessors ()

        queue_list = list (queues) if queues else ALL_QUEUES
        click.echo (f"Starting worker for queues: {', '.join (queue_list)}")

        if max_jobs:
            click.echo (f"Max concurrent jobs: {max_jobs}")
        if worker_ttl:
            click.echo (f"Worker TTL: {worker_ttl}s")

        worker = AppQueueProcessor.startWorker (*queue_list, max_jobs=max_jobs, default_worker_ttl=worker_ttl)
        click.echo ("Worker started. Press Ctrl+C to stop.")
        worker.work ()

    except KeyboardInterrupt:
        click.echo ("\nWorker stopped by user.")
        sys.exit (0)
    except Exception as e:
        click.echo (f"Error: {e}", err=True)
        import traceback
        traceback.print_exc ()
        sys.exit (1)
