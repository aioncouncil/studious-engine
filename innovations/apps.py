from django.apps import AppConfig


class InnovationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'innovations'
    verbose_name = 'Innovation System'

    def ready(self):
        try:
            import innovations.signals  # noqa F401
        except ImportError:
            pass
