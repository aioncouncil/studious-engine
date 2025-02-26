from django.apps import AppConfig


class ZonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zones'
    verbose_name = 'Zones Management'

    def ready(self):
        try:
            import zones.signals  # noqa F401
        except ImportError:
            pass
