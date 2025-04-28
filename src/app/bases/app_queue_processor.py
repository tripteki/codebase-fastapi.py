import logging
from typing import Dict, Callable, Optional
import importlib
from rq import Worker
from src.app.bases.app_queue import AppQueue, Processor, Process
from src.app.utils.app_module_scanner import AppModuleScanner

logger = logging.getLogger (__name__)

class AppQueueProcessor:
    """
    AppQueueProcessor

    Attributes:
        _processors (Dict[str, Dict[str, Callable[..., object]]])
    """
    _processors: Dict[str, Dict[str, Callable[..., object]]] = {}

    @staticmethod
    def loadProcessors () -> None:
        """
        Args:
            None
        Returns:
            None
        """
        def onModuleLoaded (moduleName: str) -> None:
            """
            Args:
                moduleName (str)
            Returns:
                None
            """
            try:
                module = importlib.import_module (moduleName)
                for attrName in dir (module):
                    if attrName.startswith ("_"):
                        continue
                    attr = getattr (module, attrName)
                    if isinstance (attr, type) and hasattr (attr, "_queue_name"):
                        queueName = attr._queue_name
                        if queueName not in AppQueueProcessor._processors:
                            AppQueueProcessor._processors[queueName] = {}
                        for methodName in dir (attr):
                            if methodName.startswith ("_"):
                                continue
                            method = getattr (attr, methodName)
                            if callable (method) and hasattr (method, "_job_name"):
                                jobName = method._job_name
                                AppQueueProcessor._processors[queueName][jobName] = method
                                logger.info (
                                    f"Queue processor registered: {queueName}.{jobName} from {moduleName}"
                                )
            except Exception as e:
                logger.warning (
                    f"Could not process queue processor from {moduleName}: {e}",
                    exc_info=True
                )

        loaded = AppModuleScanner.scanModules ("processors", callback=onModuleLoaded)
        logger.info (f"Loaded {len (loaded)} queue processor module(s)")

    @staticmethod
    def getHandler (queueName: str, jobName: str) -> Optional[Callable[..., object]]:
        """
        Args:
            queueName (str)
            jobName (str)
        Returns:
            Optional[Callable[..., object]]
        """
        if queueName in AppQueueProcessor._processors and jobName in AppQueueProcessor._processors[queueName]:
            return AppQueueProcessor._processors[queueName][jobName]
        return None

    @staticmethod
    def startWorker (
        queueName: str,
        *queueNames: str,
        max_jobs: Optional[int] = None,
        default_worker_ttl: Optional[int] = None
    ) -> Worker:
        """
        Args:
            queueName (str)
            *queueNames (str)
            max_jobs (Optional[int])
            default_worker_ttl (Optional[int])
        Returns:
            Worker
        """
        queueNamesList = [queueName] + list (queueNames)
        queues = [AppQueue.getQueue (name) for name in queueNamesList]

        worker_kwargs = {
            "connection": AppQueue.connection (),
        }

        if max_jobs is not None:
            worker_kwargs["max_jobs"] = max_jobs

        if default_worker_ttl is not None:
            worker_kwargs["default_worker_ttl"] = default_worker_ttl

        worker = Worker (queues, **worker_kwargs)
        return worker
