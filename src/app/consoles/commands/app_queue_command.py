import click
import sys
from src.app.bases.app_console import Command
from src.app.bases.app_event_listener import AppEventListener
from src.app.bases.app_queue_processor import AppQueueProcessor
from src.app.constants.queue_constants import ALL_QUEUES, USER_ADMIN_QUEUE, NOTIFICATION_QUEUE

@Command (name="queue:work", help="Start queue worker for processing background jobs")
@click.argument ("queues", nargs=-1)
def queueWorkCommand (queues):
    """
    Start queue worker for processing background jobs

    Usage:
        poetry run python3 src/cli.py queue:work
        poetry run python3 src/cli.py queue:work {worker_queue_name}
    """
    try:
        click.echo ("Loading event listeners...")
        AppEventListener.loadListeners (None)

        click.echo ("Loading queue processors...")
        AppQueueProcessor.loadProcessors ()

        queue_list = list (queues) if queues else ALL_QUEUES
        click.echo (f"Starting worker for queues: {', '.join (queue_list)}")

        worker = AppQueueProcessor.startWorker (*queue_list)
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
