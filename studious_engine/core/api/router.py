from rest_framework import routers

from .base import (
    PlayerProfileViewSet,
    MarketItemViewSet,
    WishlistViewSet
)

from .art import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    ArtViewSet,
    ArtTaxonomyViewSet,
    ArtMasteryViewSet,
    TechTreeViewSet
)

# Create a router for core app
core_router = routers.DefaultRouter()

# Register existing viewsets
core_router.register(r'profiles', PlayerProfileViewSet, basename='profile')
core_router.register(r'market', MarketItemViewSet, basename='market')
core_router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# Register Art System viewsets
core_router.register(r'arts', ArtViewSet, basename='art')
core_router.register(r'art-taxonomy', ArtTaxonomyViewSet, basename='art-taxonomy')
core_router.register(r'art-mastery', ArtMasteryViewSet, basename='art-mastery')
core_router.register(r'tech-trees', TechTreeViewSet, basename='tech-tree') 