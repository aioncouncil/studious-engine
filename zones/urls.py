# studious_engine/zones/urls.py
from django.urls import path

from . import views

app_name = "zones"
urlpatterns = [
    path('', views.SectorListView.as_view(), name='sector_list'),
    path('sectors/<int:pk>/', views.SectorDetailView.as_view(), name='sector_detail'),
    path('zones/<int:pk>/', views.ZoneDetailView.as_view(), name='zone_detail'),
    path('zones/<int:pk>/contribute/', views.ZoneContributeView.as_view(), name='zone_contribute'),
]