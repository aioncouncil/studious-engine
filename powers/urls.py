from django.urls import path
from . import views

app_name = "powers"
urlpatterns = [
    path('', views.PowerListView.as_view(), name='power_list'),
    path('<int:pk>/', views.PowerDetailView.as_view(), name='power_detail'),
    path('<int:pk>/upgrade/', views.PowerUpgradeView.as_view(), name='power_upgrade'),
    path('<int:pk>/use/', views.PowerUseView.as_view(), name='power_use'),
]
