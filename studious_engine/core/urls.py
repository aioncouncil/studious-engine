# studious_engine/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views
from .views.core import toggle_wishlist, view_wishlist, update_player_location, LegacyMapView
from .api.router import core_router
from .views.art import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    ArtPokedexView, ArtDetailView, ArtDiscoverView, LogPracticeView,
    TechTreeView, TechTreeDetailView, ArtMasteryDetailView, ArtMasteryStatsView,
    ArtMasteryDashboardView
)

app_name = "core"
urlpatterns = [
    path('', views.PublicStoreView.as_view(), name='dashboard'),
    path('profile/', login_required(views.PlayerProfileView.as_view()), name='player_profile'),
    path('map/', views.MapView.as_view(), name='map'),
    path('legacy-map/', LegacyMapView.as_view(), name='legacy_map'),
    path('nearby/', views.NearbyView.as_view(), name='nearby'),
    path('location/update/', update_player_location, name='update_location'),
    path('market/', views.StoreView.as_view(), name='market'),
    path('market/about/', views.AboutView.as_view(), name='about'),
    path('market/item/<uuid:item_id>/', views.MarketItemDetailView.as_view(), name='market_item_detail'),
    path('market/purchase/<uuid:item_id>/', views.purchase_item, name='purchase_item'),
    path('zone/', views.ZoneView.as_view(), name='zone'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('virtues/', views.VirtuesView.as_view(), name='virtues'),
    path('wishlist/', view_wishlist, name='wishlist'),
    path('wishlist/toggle/', toggle_wishlist, name='toggle_wishlist'),
    
    # Art System URLs
    path('arts/', login_required(ArtPokedexView.as_view()), name='arts_pokedex'),
    path('arts/<uuid:art_id>/', login_required(ArtDetailView.as_view()), name='art_detail'),
    path('arts/<uuid:art_id>/discover/', login_required(ArtDiscoverView.as_view()), name='art_discover'),
    path('arts/<uuid:art_id>/log-practice/', login_required(LogPracticeView.as_view()), name='log_practice'),
    path('mastery/dashboard/', login_required(ArtMasteryDashboardView.as_view()), name='art_mastery_dashboard'),
    path('mastery/<uuid:mastery_id>/', login_required(ArtMasteryDetailView.as_view()), name='art_mastery_detail'),
    path('mastery/stats/', login_required(ArtMasteryStatsView.as_view()), name='art_mastery_stats'),
    path('tech-tree/', login_required(TechTreeView.as_view()), name='tech_tree'),
    path('tech-tree/<uuid:tech_tree_id>/', login_required(TechTreeDetailView.as_view()), name='tech_tree_detail'),
    
    # API endpoints
    path('api/', include(core_router.urls)),
]