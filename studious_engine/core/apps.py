# studious_engine/core/apps.py
from django.apps import AppConfig

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class CoreConfig(AppConfig):
    name = "core"  # Changed to "core" to match the import patterns used in models
    verbose_name = "Core Game Mechanics"

    def ready(self):
        try:
            import core.signals  # noqa F401
        except ImportError:
            pass