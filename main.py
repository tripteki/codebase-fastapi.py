from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
import socketio
from src.app.configs.app_config import AppConfig
from src.app.configs.swagger_config import SwaggerConfig
from src.app.configs.playground_config import PlaygroundConfig
from src.app.bases.app_log import AppLog
from src.app.bases.app_view import AppView
from src.app.bases.app_static import AppStatic
from src.app.bases.app_http import AppHttp
from src.app.bases.app_cache import AppCache
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_context import AppContext
from src.app.bases.app_event_listener import AppEventListener
from src.app.bases.app_queue_processor import AppQueueProcessor
from src.app.bases.app_scheduler import AppScheduler
from src.app.bases.app_schedule_loader import AppScheduleLoader
from src.app.routes.app_http_router import AppHttpRouter as AppHttpRouterProvider
from src.app.routes.app_ws_router import AppWsRouter as AppWsRouterProvider, getSocketIOServer
from fastapi.exceptions import HTTPException
from src.app.exceptions.validation_exception_handler import validationExceptionHandler
from src.app.exceptions.http_exception_handler import httpExceptionHandler
from src.app.exceptions.general_exception_handler import generalExceptionHandler

appConfig = AppConfig.config ()
swaggerConfig = SwaggerConfig.config ()
playgroundConfig = PlaygroundConfig.config ()

swagger_path = swaggerConfig.swagger_path
if not swagger_path.startswith ("/"):
    swagger_path = f"/{swagger_path}"

playground_path = playgroundConfig.playground_path
if not playground_path.startswith ("/"):
    playground_path = f"/{playground_path}"

@asynccontextmanager
async def lifespan (app: FastAPI):
    """
    Lifespan context manager for FastAPI application startup and shutdown
    """
    app.state.log = AppLog.register (app)
    app.state.view = AppView.register (app)

    try:
        app.state.cacheRedis = await AppCache.cache (app)
    except Exception:
        app.state.cacheRedis = None
    try:
        app.state.databasePostgresql = await AppDatabase.databasePostgresqlInit (app)
    except Exception:
        app.state.databasePostgresql = None
    try:
        app.state.databaseMongodb = AppDatabase.databaseMongonosql ()
    except Exception:
        app.state.databaseMongodb = None

    AppScheduler.start ()

    yield

    AppScheduler.shutdown ()
    if hasattr (app.state, "cacheRedis") and app.state.cacheRedis:
        await app.state.cacheRedis.aclose ()
    if hasattr (app.state, "databasePostgresql") and app.state.databasePostgresql:
        pass
    if hasattr (app.state, "databaseMongodb") and app.state.databaseMongodb:
        await AppDatabase.databaseMongonosqlClose ()
    app.state.log = None
    app.state.view = None
    app.state.cacheRedis = None
    app.state.databasePostgresql = None
    app.state.databaseMongodb = None

app = FastAPI (
    title=appConfig.app_name.title (),
    description=swaggerConfig.swagger_description,
    version=appConfig.app_version,
    docs_url=swagger_path,
    redoc_url=None,
    lifespan=lifespan,
)

AppContext.setApp (app)

app.add_exception_handler (RequestValidationError, validationExceptionHandler)
app.add_exception_handler (HTTPException, httpExceptionHandler)
app.add_exception_handler (Exception, generalExceptionHandler)

##################################

AppEventListener.loadListeners (app)
AppQueueProcessor.loadProcessors ()
AppScheduleLoader.loadSchedules ()

AppHttpRouterProvider.route (app)
AppWsRouterProvider.route (app)

##################################

AppStatic.boot (app)
AppHttp.boot (app)

##################################

if __name__ == "__main__":
    AppHttp.register (app)
