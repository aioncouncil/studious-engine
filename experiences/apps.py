# studious_engine/experiences/apps.py
from django.apps import AppConfig


class ExperiencesConfig(AppConfig):
    name = "experiences"
    verbose_name = "Experience System"

    def ready(self):
        try:
            import experiences.signals  # noqa F401
        except ImportError:
            pass


# studious_engine/zones/apps.py
from django.apps import AppConfig


class ZonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studious_engine.zones'
    verbose_name = 'Zones Management'

    def ready(self):
        try:
            import studious_engine.zones.signals  # noqa F401
        except ImportError:
            pass


# studious_engine/powers/apps.py
from django.apps import AppConfig


class PowersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studious_engine.powers'
    verbose_name = 'Powers System'

    def ready(self):
        try:
            import studious_engine.powers.signals  # noqa F401
        except ImportError:
            pass


# studious_engine/innovations/apps.py
from django.apps import AppConfig


class InnovationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studious_engine.innovations'
    verbose_name = 'Innovation System'

    def ready(self):
        try:
            import studious_engine.innovations.signals  # noqa F401
        except ImportError:
            pass