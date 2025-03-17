# Import all views from the views module and expose them at the package level
from .core import (
    GameDashboardView, PlayerProfileView, MapView, NearbyView, 
    StoreView, MarketItemDetailView, purchase_item, AboutView,
    ZoneView, NotificationsView, toggle_wishlist, view_wishlist, VirtuesView
)

from .art import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    ArtPokedexView, ArtDetailView, ArtDiscoverView, LogPracticeView,
    TechTreeView, TechTreeDetailView, ArtMasteryDetailView, ArtMasteryStatsView
)

__all__ = [
    'GameDashboardView', 'PlayerProfileView', 'MapView', 'NearbyView',
    'StoreView', 'MarketItemDetailView', 'purchase_item', 'AboutView',
    'ZoneView', 'NotificationsView', 'toggle_wishlist', 'view_wishlist', 'VirtuesView',
    'ArtPokedexView', 'ArtDetailView', 'ArtDiscoverView', 'LogPracticeView',
    'TechTreeView', 'TechTreeDetailView', 'ArtMasteryDetailView', 'ArtMasteryStatsView'
]
