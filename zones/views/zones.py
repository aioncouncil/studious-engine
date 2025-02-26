from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib import messages
from django.http import JsonResponse

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