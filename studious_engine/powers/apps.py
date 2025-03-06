from django.apps import AppConfig


class PowersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'powers'
    verbose_name = 'Powers System'

    def ready(self):
        try:
            import powers.signals  # noqa F401
        except ImportError:
            pass
