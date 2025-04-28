from fastapi import FastAPI
from src.app.controllers.app_controller import appRouter
from src.v1.api.notification.controllers.notification_admin_controller import notificationAdminRouter
from src.v1.api.notification.controllers.notification_user_controller import notificationUserRouter
from src.v1.api.user.controllers.user_admin_controller import userAdminRouter
from src.v1.api.user.controllers.user_auth_controller import userAuthRouter, userAuthPublicRouter

class AppHttpRouter:
    """
    AppHttpRouter
    """
    @staticmethod
    def route (app: FastAPI) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        app.include_router (appRouter)
        app.include_router (userAuthPublicRouter)
        app.include_router (userAuthRouter)
        app.include_router (userAdminRouter)
        app.include_router (notificationUserRouter)
        app.include_router (notificationAdminRouter)
