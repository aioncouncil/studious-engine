# studious_engine/experiences/urls.py
from django.urls import path
# Import specific view classes and functions directly from views.py
from experiences.views import (

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    ExperienceListView, 
    ExperienceDetailView, 
    JoinExperienceView, 
    UpdateExperienceStatusView,
    PowerListView,
    PowerDetailView,
    submit_experience,
    experience_submitted,
    ExperienceInstanceListView,
    ExperienceInstanceDetailView,
    CreateExperienceInstanceView,
    UpdateExperienceInstanceView,
    join_experience_instance,
    withdraw_from_experience_instance,
    advance_matrix_phase
)

app_name = "experiences"
urlpatterns = [
    # Experience views
    path('', ExperienceListView.as_view(), name='experience_list'),
    path('<int:pk>/', ExperienceDetailView.as_view(), name='experience_detail'),
    path('submit/', submit_experience, name='submit_experience'),
    path('submitted/', experience_submitted, name='experience_submitted'),
    path('<int:pk>/join/', JoinExperienceView.as_view(), name='join_experience'),
    path('<int:experience_id>/update/', UpdateExperienceStatusView.as_view(), name='update_experience'),
    
    # Power views
    path('powers/', PowerListView.as_view(), name='power_list'),
    path('powers/<int:pk>/', PowerDetailView.as_view(), name='power_detail'),
    
    # Experience Instance views
    path('instances/', ExperienceInstanceListView.as_view(), name='instance_list'),
    path('instances/<uuid:pk>/', ExperienceInstanceDetailView.as_view(), name='instance_detail'),
    path('instances/create/', CreateExperienceInstanceView.as_view(), name='create_instance'),
    path('instances/<uuid:pk>/edit/', UpdateExperienceInstanceView.as_view(), name='edit_instance'),
    path('instances/<uuid:pk>/join/', join_experience_instance, name='join_instance'),
    path('instances/<uuid:pk>/withdraw/', withdraw_from_experience_instance, name='withdraw_instance'),
    path('instances/<uuid:pk>/advance-phase/', advance_matrix_phase, name='advance_phase'),
]