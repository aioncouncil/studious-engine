from django.urls import path
from . import views

app_name = 'physics'

urlpatterns = [
    path('simulations/', views.simulation_list, name='simulation_list'),
    path('simulations/create/', views.simulation_create, name='simulation_create'),
    path('simulations/<uuid:simulation_id>/', views.simulation_detail, name='simulation_detail'),
    path('interactions/<uuid:interaction_id>/end/', views.end_interaction, name='end_interaction'),
    path('api/simulations/<uuid:simulation_id>/', views.simulation_api, name='simulation_api'),
] 