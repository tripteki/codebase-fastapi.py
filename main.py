from fastapi import FastAPI
from src.app.configs.app_config import AppConfig
from src.app.configs.swagger_config import SwaggerConfig
from src.app.configs.playground_config import PlaygroundConfig
from src.app.bases.app_log import AppLog
from src.app.bases.app_view import AppView
from src.app.bases.app_static import AppStatic
from src.app.bases.app_http import AppHttp
from src.app.bases.app_cache import AppCache
from src.app.bases.app_database import AppDatabase
from src.app.routes.app_http_router import AppHttpRouter as AppHttpRouterProvider
from src.app.routes.app_ws_router import AppWsRouter as AppWsRouterProvider

appConfig = AppConfig.config ()
swaggerConfig = SwaggerConfig.config ()
playgroundConfig = PlaygroundConfig.config ()

app = FastAPI (
    title=appConfig.app_name.title (),
    description=swaggerConfig.swagger_description,
    version=appConfig.app_version
)

@app.on_event ("startup")
async def startup ():
    app.state.log = AppLog.register (app)
    app.state.view = AppView.register (app)
    app.state.cacheRedis = await AppCache.cache (app)
    app.state.databasePostgresql = await AppDatabase.database (app)

@app.on_event ("shutdown")
async def shutdown ():
    app.state.log = None
    app.state.view = None
    app.state.cacheRedis = None
    app.state.databasePostgresql = None

##################################

AppHttpRouterProvider.route (app)
AppWsRouterProvider.route (app)

##################################

AppStatic.boot (app)
AppHttp.boot (app)

if __name__ == "__main__":
    AppHttp.register (app)
