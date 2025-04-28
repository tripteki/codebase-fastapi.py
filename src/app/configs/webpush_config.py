from src.app.bases.app_config import AppConfig

class WebpushConfig (AppConfig):
    """
    WebpushConfig (AppConfig)

    Attributes:
        vapid_subject (str)
        vapid_public_key (str)
        vapid_private_key (str)
        webpush_db_table (str)
        webpush_automatic_padding (bool)
        webpush_notification_queue (str)
    """
    vapid_subject: str = ""
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    webpush_db_table: str = "push_subscriptions"
    webpush_automatic_padding: bool = True
    webpush_notification_queue: str = "notifications"
