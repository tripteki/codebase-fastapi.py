from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from src.app.configs.app_config import AppConfig

class AppHttp:
    """
    AppHttp
    """
    @classmethod
    def register (cls, app: FastAPI) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        appConfig = AppConfig.config ()

        uvicorn.run (app,
                     host=appConfig.app_host,
                     port=appConfig.app_port,
                     debug=True)

    @classmethod
    def boot (cls, app: FastAPI) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        cls.bootCors (app)
        cls.bootCompression (app)

    @classmethod
    def bootCors (cls, app: FastAPI) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        appConfig = AppConfig.config ()

        app.add_middleware (CORSMiddleware,
                            allow_origins=appConfig.cors_origin,
                            allow_methods=appConfig.cors_methods,
                            allow_headers=appConfig.cors_allowed_headers,
                            expose_headers=appConfig.cors_exposed_headers,
                            max_age=appConfig.cors_max_age,
                            allow_credentials=appConfig.cors_credential
        )

    @classmethod
    def bootCompression (cls, app: FastAPI) -> None:
        """
        Args:
            cls
            app (FastAPI)
        Returns:
            None
        """
        appConfig = AppConfig.config ()

        if appConfig.app_env == "production":
            app.add_middleware (GZipMiddleware,
                                minimum_size=1000,
                                compresslevel=5
            )
