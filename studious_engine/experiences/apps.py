# studious_engine/experiences/apps.py
from django.apps import AppConfig


class ExperiencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
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

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class InnovationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studious_engine.innovations'
    verbose_name = 'Innovation System'

    def ready(self):
        try:
            import studious_engine.innovations.signals  # noqa F401
        except ImportError:
            pass