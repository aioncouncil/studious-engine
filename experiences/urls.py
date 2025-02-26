# studious_engine/experiences/urls.py
from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView

# Temporary placeholder views
def experience_list(request):
    return HttpResponse("Experience List")

def experience_detail(request, pk):
    return HttpResponse(f"Experience Detail {pk}")

def join_experience(request, pk):
    return HttpResponse(f"Join Experience {pk}")

def update_experience(request, experience_id):
    return HttpResponse(f"Update Experience {experience_id}")

def power_list(request):
    return HttpResponse("Power List")

def power_detail(request, pk):
    return HttpResponse(f"Power Detail {pk}")

app_name = "experiences"
urlpatterns = [
    path('', experience_list, name='experience_list'),
    path('<int:pk>/', experience_detail, name='experience_detail'),
    path('<int:pk>/join/', join_experience, name='join_experience'),
    path('<int:experience_id>/update/', update_experience, name='update_experience'),
    
    path('powers/', power_list, name='power_list'),
    path('powers/<int:pk>/', power_detail, name='power_detail'),
]