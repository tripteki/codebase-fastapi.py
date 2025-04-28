from pathlib import Path
from typing import Any, Dict, Callable, Optional
import importlib
from rq import Worker
import traceback
from src.app.bases.app_queue import AppQueue, Processor, Process

class AppQueueProcessor:
    """
    AppQueueProcessor
    """
    _processors: Dict[str, Dict[str, Callable]] = {}

    @staticmethod
    def loadProcessors () -> None:
        """
        Args:
            None
        Returns:
            None
        """
        basePath = Path (".")
        srcPath = basePath / "src"
        if not srcPath.exists ():
            return
        for item in srcPath.iterdir ():
            if not item.is_dir () or not item.name.startswith ("v") or not item.name[1:].isdigit ():
                continue
            for subPath in ["api", "graphql"]:
                targetPath = item / subPath
                if not targetPath.exists ():
                    continue
                for moduleDir in targetPath.iterdir ():
                    if not moduleDir.is_dir () or moduleDir.name.startswith ("__"):
                        continue
                    processorsDir = moduleDir / "processors"
                    if not processorsDir.exists ():
                        continue
                    for file in processorsDir.glob ("*.py"):
                        if file.name.startswith ("__"):
                            continue
                        relativePath = file.relative_to (basePath / "src")
                        moduleParts = list (relativePath.with_suffix ("").parts)
                        moduleName = "src." + ".".join (moduleParts)
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
                                            print (f"Queue processor registered: {queueName}.{jobName} from {moduleName}.")
                        except Exception as e:
                            print (f"Warning: Could not load queue processor from {file.name}: {e}.")

    @staticmethod
    def getHandler (queueName: str, jobName: str) -> Optional[Callable]:
        """
        Args:
            queueName (str)
            jobName (str)
        Returns:
            Optional[Callable]
        """
        if queueName in AppQueueProcessor._processors and jobName in AppQueueProcessor._processors[queueName]:
            return AppQueueProcessor._processors[queueName][jobName]
        return None

    @staticmethod
    def startWorker (queueName: str, *queueNames: str) -> Worker:
        """
        Args:
            queueName (str)
            *queueNames (str)
        Returns:
            Worker
        """
        queueNamesList = [queueName] + list (queueNames)
        queues = [AppQueue.getQueue (name) for name in queueNamesList]
        worker = Worker (queues, connection=AppQueue.connection ())
        return worker
