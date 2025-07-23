from django.apps import AppConfig


class DbLoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'db_logger'
    verbose_name = "DB Логгер"
