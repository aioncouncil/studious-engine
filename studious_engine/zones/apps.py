from django.apps import AppConfig

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class ZonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zones'
    verbose_name = 'Zones Management'

    def ready(self):
        try:
            import zones.signals  # noqa F401
        except ImportError:
            pass
