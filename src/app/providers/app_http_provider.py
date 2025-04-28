import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.app.bases.app_provider import AppProvider

class AppHttpProvider (AppProvider):
    """
    AppHttpProvider (AppProvider)
    """
    @staticmethod
    def register (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        uvicorn.run (app,
                     host=AppHttpProvider.appConfig ().app_host,
                     port=AppHttpProvider.appConfig ().app_port,
                     debug=True)

    @staticmethod
    def boot (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        AppHttpProvider.bootCors (app)
        AppHttpProvider.bootCsrf (app)
        AppHttpProvider.bootRatelimit (app)
        AppHttpProvider.bootCompression (app)

    @staticmethod
    def bootCors (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        if AppHttpProvider.appConfig ().app_env == "production":
            app.add_middleware (CORSMiddleware,
                                allow_origins=AppHttpProvider.appConfig ().cors_origin,
                                allow_methods=AppHttpProvider.appConfig ().cors_methods,
                                allow_headers=AppHttpProvider.appConfig ().cors_allowed_headers,
                                expose_headers=AppHttpProvider.appConfig ().cors_exposed_headers,
                                max_age=AppHttpProvider.appConfig ().cors_maxAge,
                                allow_credentials=AppHttpProvider.appConfig ().cors_credential
            )

    @staticmethod
    def bootCsrf (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        pass

    @staticmethod
    def bootRatelimit (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        pass

    @staticmethod
    def bootCompression (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        if AppHttpProvider.appConfig ().app_env == "production":
            app.add_middleware (GZipMiddleware,
                                minimum_size=1000,
                                compresslevel=5
            )
