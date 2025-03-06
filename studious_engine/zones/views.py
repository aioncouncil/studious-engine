# zones/views.py
# This file is now deprecated in favor of the zones/views/ package
# For compatibility, we import the views from the new module

from zones.views.zones import * 

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Sector, Zone

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class SectorListView(LoginRequiredMixin, ListView):
    """List all sectors."""
    model = Sector
    template_name = 'zones/sector_list.html'
    context_object_name = 'sectors'
    
    def get_queryset(self):
        """Return all sectors."""
        # Get base queryset
        queryset = Sector.objects.all()
        
        # If no sectors found in database, generate sample sectors
        if not queryset.exists():
            # Check if we need to create sample sectors
            if Sector.objects.count() == 0:
                # Create sample sectors
                sample_sectors = [
                    {
                        'name': 'Academic Zone',
                        'description': 'The center of campus learning and research activities.',
                        'is_active': True,
                    },
                    {
                        'name': 'Innovation Commons',
                        'description': 'A collaborative space for creative thinking and ideation.',
                        'is_active': True,
                    },
                    {
                        'name': 'Student Life Hub',
                        'description': 'The center of campus social activities and student services.',
                        'is_active': True,
                    },
                    {
                        'name': 'Wellness Center',
                        'description': 'Dedicated to physical and mental well-being activities.',
                        'is_active': True,
                    },
                ]
                
                for sector_data in sample_sectors:
                    Sector.objects.create(**sector_data)
                
                # Refresh queryset after creating sample sectors
                queryset = Sector.objects.all()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add zones to context."""
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        return context 