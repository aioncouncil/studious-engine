# studious_engine/zones/urls.py
from django.urls import path

from . import views
from zones.views import zones

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

app_name = "zones"
urlpatterns = [
    path('', views.SectorListView.as_view(), name='sector_list'),
    path('sectors/<int:pk>/', views.SectorDetailView.as_view(), name='sector_detail'),
    path('zones/<int:pk>/', views.ZoneDetailView.as_view(), name='zone_detail'),
    path('zones/<int:pk>/contribute/', views.ZoneContributeView.as_view(), name='zone_contribute'),
    path('api/map-elements/', zones.map_elements_api, name='map_elements_api'),
    
    # New URLs for zone submission
    path('zones/submit/', zones.submit_zone, name='submit_zone'),
    path('zones/submitted/', zones.zone_submitted, name='zone_submitted'),
]