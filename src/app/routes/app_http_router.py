from src.app.controllers.app_controller import appRouter

class AppHttpRouter:
    """
    AppHttpRouter
    """
    @staticmethod
    def route (app) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        app.include_router (appRouter)
