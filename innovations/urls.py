# studious_engine/innovations/urls.py
from django.urls import path

from . import views

app_name = "innovations"
urlpatterns = [
    path('', views.InnovationListView.as_view(), name='innovation_list'),
    path('<int:pk>/', views.InnovationDetailView.as_view(), name='innovation_detail'),
    path('create/', views.InnovationCreateView.as_view(), name='innovation_create'),
    path('<int:pk>/contribute/', views.InnovationContributeView.as_view(), name='innovation_contribute'),
    path('tech-tree/', views.TechTreeView.as_view(), name='tech_tree'),
    path('tech-tree/node/<int:pk>/', views.TechTreeNodeDetailView.as_view(), name='tech_tree_node_detail'),
]