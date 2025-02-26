# studious_engine/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"  # Changed to "core" to match the import patterns used in models
    verbose_name = "Core Game Mechanics"

    def ready(self):
        try:
            import core.signals  # noqa F401
        except ImportError:
            pass