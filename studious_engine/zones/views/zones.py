from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib import messages
from django.http import JsonResponse
from experiences.models import Experience
from zones.models import Zone
from django.db import models
from zones.forms import ZoneForm

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

# Temporary stub models for development
class MockSector:
    def __init__(self, id):
        self.id = id
        self.name = f'Sector {id}'
        self.description = f'Description for Sector {id}'
        self.zones_count = 3
        self.rank = id
        
    def get_number_display(self):
        return f"S{self.id}"

class MockZone:
    def __init__(self, id):
        sector_id = id // 10
        zone_number = id % 10
        
        self.id = id
        self.zone_number = zone_number
        self.zone_type = f"Zone Type {zone_number}"
        self.area = "large"
        self.rank = sector_id
        self.sector = MockSector(sector_id)
        
    def get_area_display(self):
        return "Large"
        
    def get_rank_display(self):
        return f"Rank {self.rank}"


class SectorListView(LoginRequiredMixin, ListView):
    """List all sectors in the game."""
    template_name = 'zones/sector_list.html'
    context_object_name = 'sectors'
    
    def get_queryset(self):
        # Stub implementation
        return [MockSector(i) for i in range(1, 5)]


class SectorDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific sector."""
    template_name = 'zones/sector_detail.html'
    context_object_name = 'sector'
    
    def get_object(self, queryset=None):
        # Stub implementation
        sector_id = self.kwargs.get('pk')
        sector = MockSector(sector_id)
        
        # Add zones to the sector
        sector.zones = [
            MockZone(sector_id * 10 + j) for j in range(1, 4)
        ]
        
        return sector


class ZoneDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific zone."""
    template_name = 'zones/zone_detail.html'
    context_object_name = 'zone'
    
    def get_object(self, queryset=None):
        # Stub implementation
        zone_id = self.kwargs.get('pk')
        return MockZone(zone_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stub implementations of additional context
        context.update({
            'zone_leaders': [],
            'player_contribution': {
                'think_tank_contributions': 45,
                'production_tank_contributions': 30,
                'overall_influence': 37.5,
                'is_zone_leader': False,
                'leadership_start_date': None
            },
            'happiness': {
                'wisdom': 65,
                'courage': 70,
                'temperance': 55,
                'justice': 60,
                'soul_average': 62.5,
                'strength': 75,
                'wealth': 50,
                'beauty': 65,
                'health': 80,
                'body_average': 67.5,
                'resources': 60,
                'friendships': 75,
                'honors': 45,
                'glory': 50,
                'environment_average': 57.5
            },
            'innovations': [
                {
                    'id': i,
                    'name': f'Innovation {i}',
                    'description': f'Description for Innovation {i}',
                    'current_stage': 'ideation',
                    'progress': 35 + (i * 10),
                    'get_current_stage_display': lambda: 'Ideation'
                } for i in range(1, 3)
            ],
            'experiences': [
                {
                    'id': i,
                    'name': f'Experience {i}',
                    'description': f'Description for Experience {i}',
                    'experience_type': 'quest' if i % 2 == 0 else 'challenge',
                    'matrix_position': 'soul_out' if i % 2 == 0 else 'body_out',
                    'difficulty': 5 + (i % 3),
                    'duration_minutes': 30 * i,
                    'get_experience_type_display': lambda: 'Quest' if i % 2 == 0 else 'Challenge',
                    'get_matrix_position_display': lambda: 'Soul Out' if i % 2 == 0 else 'Body Out'
                } for i in range(1, 5)
            ],
            'top_contributors': [
                {
                    'player': {
                        'user': {
                            'username': f'Player{i}'
                        }
                    },
                    'think_tank_contributions': 80 - (i * 10),
                    'production_tank_contributions': 70 - (i * 8),
                    'overall_influence': 75 - (i * 9),
                    'is_zone_leader': i == 1
                } for i in range(1, 6)
            ]
        })
        
        return context


class ZoneContributeView(LoginRequiredMixin, CreateView):
    """View for contributing to a zone's think tank or production tank."""
    template_name = 'zones/zone_contribute.html'
    
    def get(self, request, *args, **kwargs):
        zone_id = self.kwargs.get('pk')
        tank_type = request.GET.get('tank_type', 'think')  # Default to think tank
        
        # Stub implementation
        return render(request, self.template_name, {
            'zone': MockZone(zone_id),
            'tank_type': tank_type,
            'contribution_options': [
                {'id': 1, 'name': 'Small Contribution', 'points': 5, 'resource_cost': 2},
                {'id': 2, 'name': 'Medium Contribution', 'points': 10, 'resource_cost': 5},
                {'id': 3, 'name': 'Large Contribution', 'points': 20, 'resource_cost': 10}
            ]
        })
    
    def post(self, request, *args, **kwargs):
        # Stub implementation - would process contribution in real app
        return redirect('zones:zone_detail', pk=self.kwargs.get('pk'))

@login_required
def submit_zone(request):
    """View for users to submit new zones"""
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            # Set default values
            zone.rank = 1  # Start with basic rank
            zone.is_active = False  # Pending approval
            zone.save()
            
            messages.success(request, "Your zone has been submitted for review!")
            return redirect('zones:zone_submitted')
    else:
        form = ZoneForm()
    
    context = {
        'form': form,
        'google_maps_api_key': 'YOUR_API_KEY',  # You'll need to set up a Google Maps API key
    }
    return render(request, 'zones/submit_zone.html', context)

@login_required
def zone_submitted(request):
    """Confirmation page after submission"""
    return render(request, 'zones/zone_submitted.html')

def map_elements_api(request):
    """API endpoint to provide nearby zones and experiences for the map."""
    # Get player location
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if not lat or not lng:
        return JsonResponse({'error': 'Missing location parameters'})
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return JsonResponse({'error': 'Invalid location format'})
    
    # Calculate the distance in degrees (rough approximation)
    # 0.005 degrees is roughly 550 meters at the equator
    # Increasing to 0.05 degrees (about 5.5 km or 3.4 miles)
    search_radius_degrees = 0.05  # ~5.5 km
    
    # Query nearby zones from the database
    # We're looking for zones where either the city or country point is nearby
    nearby_zones = Zone.objects.filter(
        models.Q(
            city_latitude__gte=lat-search_radius_degrees,
            city_latitude__lte=lat+search_radius_degrees,
            city_longitude__gte=lng-search_radius_degrees,
            city_longitude__lte=lng+search_radius_degrees
        ) | 
        models.Q(
            country_latitude__gte=lat-search_radius_degrees,
            country_latitude__lte=lat+search_radius_degrees,
            country_longitude__gte=lng-search_radius_degrees,
            country_longitude__lte=lng+search_radius_degrees
        )
    ).select_related('sector')
    
    # Query nearby experiences from the database
    nearby_experiences = Experience.objects.filter(
        latitude__gte=lat-search_radius_degrees,
        latitude__lte=lat+search_radius_degrees,
        longitude__gte=lng-search_radius_degrees,
        longitude__lte=lng+search_radius_degrees,
        is_active=True
    )
    
    # Prepare zone data for the response
    zones_data = []
    for zone in nearby_zones:
        # Use city coordinates if available, otherwise use country coordinates
        zone_lat = zone.city_latitude if zone.city_latitude is not None else zone.country_latitude
        zone_lng = zone.city_longitude if zone.city_longitude is not None else zone.country_longitude
        
        # Skip zones without coordinates
        if zone_lat is None or zone_lng is None:
            continue
            
        # Determine the zone type for the icon
        if zone.area == 'polis':
            icon_type = 'think'
        elif zone.area == 'chora':
            icon_type = 'production'
        elif zone.area == 'agora':
            icon_type = 'market'
        else:
            icon_type = 'think'  # Default fallback
        
        zones_data.append({
            "id": zone.id,
            "name": f"{zone.zone_type} ({zone.get_area_display()})",
            "type": icon_type,
            "lat": zone_lat,
            "lng": zone_lng,
            "rank": zone.rank
        })
    
    # Prepare experience data for the response
    experiences_data = []
    for exp in nearby_experiences:
        # Skip experiences without coordinates
        if exp.latitude is None or exp.longitude is None:
            continue
            
        experiences_data.append({
            "id": exp.id,
            "name": exp.name,
            "type": exp.experience_type,
            "difficulty": exp.difficulty,
            "duration": exp.duration_minutes,
            "lat": exp.latitude,
            "lng": exp.longitude
        })
    
    # If no real data is found, provide a few sample items for demonstration
    if not zones_data:
        zones_data = generate_sample_zones(lat, lng)
    
    if not experiences_data:
        experiences_data = generate_sample_experiences(lat, lng)
    
    return JsonResponse({
        "zones": zones_data,
        "experiences": experiences_data
    })

def generate_sample_zones(lat, lng):
    """Generate sample zones for demonstration purposes."""
    sample_zones = []
    for i, type_data in enumerate([
        {"type": "think", "name": "Think Tank: Philosophy"},
        {"type": "production", "name": "Production Tank: Engineering"},
        {"type": "market", "name": "Agora Market: Central"}
    ]):
        # Generate positions in different directions around the player
        offset_lat = 0.001 * (i % 3 - 1)
        offset_lng = 0.001 * ((i+1) % 3 - 1)
        
        sample_zones.append({
            "id": i+1000,  # Use high IDs to avoid conflict with real data
            "name": type_data["name"],
            "type": type_data["type"],
            "lat": lat + offset_lat,
            "lng": lng + offset_lng,
            "rank": (i % 4) + 1
        })
    
    return sample_zones

def generate_sample_experiences(lat, lng):
    """Generate sample experiences for demonstration purposes."""
    sample_experiences = []
    for i, name in enumerate([
        "Quest: Campus Cleanup", 
        "Challenge: Mathematics",
        "Collaboration: Community Garden"
    ]):
        # Alternate positions
        offset_lat = 0.0005 * ((i+2) % 3 - 1)
        offset_lng = 0.0005 * (i % 3 - 1)
        
        sample_experiences.append({
            "id": i+1000,  # Use high IDs to avoid conflict with real data
            "name": name,
            "type": "quest" if "Quest" in name else "challenge" if "Challenge" in name else "collaboration",
            "difficulty": (i % 5) + 3,  # 3-7 difficulty
            "duration": (i+1) * 15,     # 15-45 minutes
            "lat": lat + offset_lat,
            "lng": lng + offset_lng
        })
    
    return sample_experiences 