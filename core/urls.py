# studious_engine/core/urls.py
from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path('', views.GameDashboardView.as_view(), name='dashboard'),
    path('profile/', views.PlayerProfileView.as_view(), name='player_profile'),
    path('map/', views.MapView.as_view(), name='map'),
    path('location/update/', views.update_player_location, name='update_location'),
]