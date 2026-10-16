from fastapi import FastAPI
from src.app.controllers.app_controller import appRouter
from src.v1.api.acl.controllers.permission_admin_controller import permissionAdminRouter
from src.v1.api.acl.controllers.role_admin_controller import roleAdminRouter
from src.v1.api.dashboard.controllers.dashboard_admin_controller import dashboardAdminRouter
from src.v1.api.log.controllers.activity_admin_controller import activityAdminRouter
from src.v1.api.notification.controllers.notification_admin_controller import notificationAdminRouter
from src.v1.api.notification.controllers.notification_user_controller import notificationUserRouter
from src.v1.api.search.controllers.search_admin_controller import searchAdminRouter
from src.v1.api.setting.controllers.setting_admin_controller import settingAdminRouter
from src.v1.api.setting.controllers.setting_variables_controller import settingVariablesRouter
from src.v1.api.user.controllers.user_profile_controller import userProfileRouter
from src.v1.api.user.controllers.user_admin_controller import userAdminRouter
from src.v1.api.user.controllers.user_auth_controller import userAuthRouter, userAuthPublicRouter
from src.v1.api.user.controllers.webpush_subscription_controller import webpushSubscriptionRouter

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
        app.include_router (userProfileRouter)
        app.include_router (userAdminRouter)
        app.include_router (roleAdminRouter)
        app.include_router (permissionAdminRouter)
        app.include_router (activityAdminRouter)
        app.include_router (searchAdminRouter)
        app.include_router (webpushSubscriptionRouter)
        app.include_router (notificationUserRouter)
        app.include_router (notificationAdminRouter)
        app.include_router (dashboardAdminRouter)
        app.include_router (settingAdminRouter)
        app.include_router (settingVariablesRouter)
