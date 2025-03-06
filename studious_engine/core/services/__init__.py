# Core services package

from .user_service import UserService
from .art.art_service import ArtService
from .art.mastery_service import MasteryService
from .art.practice_service import PracticeService
from .art.tech_tree_service import TechTreeService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

__all__ = [
    'UserService',
    'ArtService',
    'MasteryService',
    'PracticeService',
    'TechTreeService',
] 