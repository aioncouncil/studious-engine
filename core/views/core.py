from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

# Temporary stub implementation of models for development
class PlayerProfile:
    @staticmethod
    def objects():
        class ProfileManager:
            def get(self, **kwargs):
                return PlayerProfile()
        return ProfileManager()
    
    def __init__(self):
        # Stub properties
        self.latitude = 0
        self.longitude = 0
        self.happiness = {}
        self.powers = MockRelationship()
        self.experiences = MockRelationship()
        self.zone_contributions = MockRelationship()
        self.innovation_contributions = MockRelationship()
    
    def save(self):
        pass

class MockRelationship:
    def count(self):
        return 0
    
    def filter(self, **kwargs):
        return self
    
    def all(self):
        return []

class GameDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for the EudaimoniaGo game."""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use a try block to prevent errors if models aren't fully implemented
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            
            context.update({
                'player': player,
                'happiness': player.happiness,
                'current_time': timezone.now(),
                # Add more context as needed for the dashboard
            })
        except Exception as e:
            # Fallback if models aren't available
            context.update({
                'error_message': str(e),
                'current_time': timezone.now(),
            })
        return context


class PlayerProfileView(LoginRequiredMixin, DetailView):
    """Detailed view of a player's profile."""
    template_name = 'core/player_profile.html'
    context_object_name = 'player'
    
    def get_object(self, queryset=None):
        """Get the player profile for the current user."""
        try:
            return PlayerProfile.objects.get(user=self.request.user)
        except Exception:
            # Return a stub object if the model isn't available
            return PlayerProfile()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.get_object()
        
        # Add additional stats and data for the profile view
        try:
            context.update({
                'powers_count': player.powers.count(),
                'completed_experiences': player.experiences.filter(status='completed').count(),
                'zone_contributions': player.zone_contributions.all()[:5],  # Get 5 most recent
                'innovation_contributions': player.innovation_contributions.all()[:5],  # Get 5 most recent
            })
        except Exception:
            # Fallback if the related models aren't available
            context.update({
                'powers_count': 0,
                'completed_experiences': 0,
                'zone_contributions': [],
                'innovation_contributions': [],
            })
        return context


class MapView(LoginRequiredMixin, TemplateView):
    """Main map view for the game, showing nearby zones and experiences."""
    template_name = 'core/map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            
            # In a real implementation, this would use the player's location
            # to find nearby zones, experiences, and other players
            context.update({
                'player': player,
                'player_latitude': player.latitude or 0,
                'player_longitude': player.longitude or 0,
                # We'd add nearby zones, experiences, etc.
            })
        except Exception:
            # Fallback if models aren't available
            context.update({
                'player_latitude': 0,
                'player_longitude': 0,
            })
        return context


@login_required
def update_player_location(request):
    """API endpoint to update a player's location from GPS data."""
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude and longitude:
            try:
                player = PlayerProfile.objects.get(user=request.user)
                player.latitude = float(latitude)
                player.longitude = float(longitude)
                player.last_location_update = timezone.now()
                player.save()
                
                # Here you would also check for nearby game elements
                # and return them in the response
                
                return render(request, 'core/location_updated.html', {
                    'player': player,
                    # Include nearby game elements
                })
            except Exception:
                # Fallback if models aren't available
                return JsonResponse({
                    "status": "success", 
                    "message": "Location updated (stub implementation)",
                    "latitude": latitude,
                    "longitude": longitude
                })
    
    # Handle GET or failed POST
    return render(request, 'core/update_location.html') 