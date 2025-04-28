from fastapi import FastAPI
from src.app.bases.app import App
from src.app.providers.app_http_provider import AppHttpProvider
from src.app.providers.app_view_provider import AppViewProvider
from src.app.routes.app_http_router import AppHttpRouter as AppHttpRouterProvider
from src.app.routes.app_ws_router import AppWsRouter as AppWsRouterProvider

app = FastAPI (
    title=App.appConfig ().app_name.title (),
    description=App.swaggerConfig ().swagger_description,
    version=App.appConfig ().app_version
)

AppHttpProvider.boot (app)
AppHttpRouterProvider.route (app)
AppWsRouterProvider.route (app)
AppViewProvider.boot (app)

if __name__ == "__main__":
    AppHttpProvider.register (app)
