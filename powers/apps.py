from django.apps import AppConfig


class PowersConfig(AppConfig):
    name = "powers"
    verbose_name = "Powers"

    def ready(self):
        try:
            import powers.signals  # noqa F401
        except ImportError:
            pass
