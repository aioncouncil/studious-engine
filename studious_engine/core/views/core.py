from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, UpdateView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Avg, Q, F, Sum
import json

# Import the real PlayerProfile model and UserService
from core.models import PlayerProfile, PlayerHappiness, UserPreferences, UserLocation, MarketItem, Wishlist
from core.services.user_service import UserService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

# Temporary stub implementation of models for development
class MockRelationship:
    def count(self):
        return 5
    
    def filter(self, **kwargs):
        return self
    
    def all(self):
        return []

class GameDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for the EudaimoniaGo game."""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_profile = PlayerProfile.objects.get(user=self.request.user)
        
        # Get the happiness metrics
        try:
            happiness = player_profile.happiness
        except PlayerHappiness.DoesNotExist:
            happiness = PlayerHappiness.objects.create(player=player_profile)
        
        # Get recent experiences
        recent_experiences = MockRelationship()  # Placeholder until Experience models are ready
        
        # Get recently practiced arts
        from core.services.art.mastery_service import MasteryService
        from core.services.art.practice_service import PracticeService
        
        # Get art mastery summary data
        mastery_summary = None
        recently_practiced_arts = []
        try:
            mastery_summary = MasteryService.get_mastery_summary(self.request.user)
            recently_practiced_arts = PracticeService.get_practice_history(
                self.request.user, limit=3
            )
        except:
            # If services aren't fully implemented or other errors occur, use empty values
            pass
        
        context.update({
            'player_profile': player_profile,
            'happiness': happiness,
            'recent_experiences': recent_experiences,
            'mastery_summary': mastery_summary,
            'recently_practiced_arts': recently_practiced_arts,
        })
        
        return context


class PlayerProfileView(LoginRequiredMixin, DetailView):
    """Detailed view of a player's profile."""
    template_name = 'core/player_profile.html'
    context_object_name = 'player_profile'
    
    def get_object(self, queryset=None):
        """Get the player profile for the current user."""
        try:
            # Get or create profile using UserService
            return UserService.create_user_profile(user=self.request.user)
        except Exception as e:
            # Fallback to a temporary profile object if there's an unexpected error
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(f"Error getting player profile: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.get_object()
        
        # Get recommendations from UserService
        recommendations = UserService.recommend_experiences(player, count=3)
        
        # Check for rank up eligibility
        rank_changed, current_rank = UserService.rank_up_check(player)
        
        # Get economic layer permissions
        economic_permissions = UserService.get_economic_layer_permissions(player)
        
        # Add additional stats and data for the profile view
        context.update({
            'powers_count': getattr(player, 'powers', MockRelationship()).count(),
            'completed_experiences': getattr(player, 'experiences', MockRelationship()).filter(status='completed').count(),
            'zone_contributions': getattr(player, 'zone_contributions', MockRelationship()).all()[:5],  # Get 5 most recent
            'innovation_contributions': getattr(player, 'innovation_contributions', MockRelationship()).all()[:5],  # Get 5 most recent
            'user': self.request.user,  # Add the user explicitly
            'recommendations': recommendations,
            'rank_changed': rank_changed,
            'economic_permissions': economic_permissions,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests to update profile."""
        player = self.get_object()
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            player.avatar = request.FILES['avatar']
        
        # Handle bio update
        if 'bio' in request.POST:
            player.bio = request.POST['bio']
            
        # Handle title update
        if 'title' in request.POST:
            player.title = request.POST['title']
        
        # Handle economic layer update (for admins)
        if request.user.is_staff and 'economic_layer' in request.POST:
            new_layer = request.POST['economic_layer']
            if new_layer in [choice[0] for choice in PlayerProfile.ECONOMIC_LAYER_CHOICES]:
                player.economic_layer = new_layer
            
        player.save()
        
        return self.get(request, *args, **kwargs)


class MapView(LoginRequiredMixin, TemplateView):
    """Main map view for the game, showing nearby zones and experiences."""
    template_name = 'core/atlantis_map.html'  # Now using the Atlantis map as default
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            player, created = PlayerProfile.objects.get_or_create(user=self.request.user)
            
            # In a real implementation, this would use the player's location
            # to find nearby zones, experiences, and other players
            context.update({
                'player': player,
                'player_latitude': player.latitude or 0,
                'player_longitude': player.longitude or 0,
                # We'd add nearby zones, experiences, etc.
            })
        except Exception as e:
            # Fallback if there's an error
            context.update({
                'player_latitude': 0,
                'player_longitude': 0,
                'error': str(e)
            })
        return context


class LegacyMapView(LoginRequiredMixin, TemplateView):
    """Legacy version of the map view for backwards compatibility."""
    template_name = 'core/map_legacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            player, created = PlayerProfile.objects.get_or_create(user=self.request.user)
            
            context.update({
                'player': player,
                'player_latitude': player.latitude or 0,
                'player_longitude': player.longitude or 0,
            })
        except Exception as e:
            context.update({
                'player_latitude': 0,
                'player_longitude': 0,
                'error': str(e)
            })
        return context


class NearbyView(LoginRequiredMixin, TemplateView):
    """View for displaying nearby locations and research tasks."""
    template_name = "core/nearby_view.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            player, created = PlayerProfile.objects.get_or_create(user=self.request.user)
            
            context.update({
                'player': player,
                # We'd fetch nearby locations here in a full implementation
            })
        except Exception as e:
            # Fallback if there's an error
            context.update({
                'error': str(e)
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
                player, created = PlayerProfile.objects.get_or_create(user=request.user)
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
            except Exception as e:
                # Return error message
                return JsonResponse({
                    "status": "error", 
                    "message": f"Error updating location: {str(e)}",
                    "latitude": latitude,
                    "longitude": longitude
                })
    
    # Handle GET or failed POST
    return render(request, 'core/update_location.html')


class StoreView(LoginRequiredMixin, TemplateView):
    """Unified Market System for all transactions, requests, and exchanges."""
    template_name = 'core/store.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            player, created = PlayerProfile.objects.get_or_create(user=self.request.user)
            
            # Get all market items
            all_items = MarketItem.objects.all()
            
            # Apply filters from request.GET
            filtered_items = self.get_filtered_items(all_items)
            
            # Get featured items
            featured_items = all_items.filter(is_featured=True)
            
            # Get items by layer
            outer_items = all_items.filter(economic_layer='outer')
            middle_items = all_items.filter(economic_layer='middle')
            inner_items = all_items.filter(economic_layer='inner')
            
            # Get user's wishlisted items
            wishlist_items = Wishlist.objects.filter(user=self.request.user).values_list('item_id', flat=True)
            
            # Get recommendations based on highest recommendation score
            recommendations = all_items.order_by('-recommendation_score')[:8]
            
            # Market layer stats
            market_layers = [
                {
                    'name': 'Port City (Outer Layer)',
                    'code': 'outer',
                    'description': 'Traditional marketplace economy for external engagement.',
                    'access_level': 'Open',
                    'items_count': outer_items.count()
                },
                {
                    'name': 'Laws Model (Middle Layer)',
                    'code': 'middle',
                    'description': 'Semi-closed economy for committed players.',
                    'access_level': 'Restricted',
                    'items_count': middle_items.count()
                },
                {
                    'name': 'Republic Model (Inner Layer)',
                    'code': 'inner',
                    'description': 'Resource sharing and common ownership.',
                    'access_level': 'Merit-Based',
                    'items_count': inner_items.count()
                }
            ]
            
            context.update({
                'player': player,
                'market_layers': market_layers,
                'featured_items': featured_items[:8],  # Limit to 8 items
                'recommendations': recommendations,
                'outer_items': outer_items[:12],  # Limit to 12 items
                'middle_items': middle_items[:12],  # Limit to 12 items
                'inner_items': inner_items[:12],  # Limit to 12 items
                'filtered_items': filtered_items[:48],  # Limit to 48 items for performance
                'wishlist_items': wishlist_items,
                'wishlist_count': len(wishlist_items),
                # Stats for market items
                'total_items_count': all_items.count(),
                'filtered_count': filtered_items.count(),
                'categories': MarketItem.CATEGORY_CHOICES
            })
        except Exception as e:
            # Fallback if there's an error
            context.update({
                'error': str(e)
            })
        return context
    
    def get_filtered_items(self, queryset):
        """Apply filters from request parameters."""
        # Get filter parameters
        search_query = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '')
        layer = self.request.GET.get('layer', '')
        sort_by = self.request.GET.get('sort', 'recommended')
        rank = self.request.GET.get('rank', '')
        availability = self.request.GET.get('availability', '')
        price_type = self.request.GET.get('price_type', '')
        
        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if layer:
            queryset = queryset.filter(economic_layer=layer)
        
        if rank:
            # Handle different rank filters
            rank_value = int(rank)
            if rank_value == 1:
                queryset = queryset.filter(min_rank_required=1)
            else:
                queryset = queryset.filter(min_rank_required__lte=rank_value)
        
        if availability:
            if availability == 'available':
                # Items with no specific end date or end date in future
                queryset = queryset.filter(
                    Q(available_until__isnull=True) | 
                    Q(available_until__gt=timezone.now())
                )
            elif availability == 'limited':
                # Items with a specific end date in the future
                queryset = queryset.filter(
                    available_until__isnull=False, 
                    available_until__gt=timezone.now()
                )
        
        if price_type:
            queryset = queryset.filter(price_type=price_type)
        
        # Apply sorting
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:  # Default to recommended
            queryset = queryset.order_by('-is_featured', '-recommendation_score')
        
        return queryset


@login_required
@require_POST
def toggle_wishlist(request):
    """API endpoint to add/remove items from the user's wishlist."""
    item_id = request.POST.get('item_id')
    
    if not item_id:
        return JsonResponse({'status': 'error', 'message': 'Item ID is required'})
    
    try:
        item = get_object_or_404(MarketItem, id=item_id)
        
        # Check if item is already in wishlist
        wishlist_entry = Wishlist.objects.filter(user=request.user, item=item)
        
        if wishlist_entry.exists():
            # Remove from wishlist
            wishlist_entry.delete()
            is_in_wishlist = False
            message = f"{item.name} removed from wishlist"
        else:
            # Add to wishlist
            Wishlist.objects.create(user=request.user, item=item)
            is_in_wishlist = True
            message = f"{item.name} added to wishlist"
        
        # Get updated wishlist count
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'is_in_wishlist': is_in_wishlist,
            'wishlist_count': wishlist_count
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def view_wishlist(request):
    """View for displaying a user's wishlist."""
    wishlist_items = MarketItem.objects.filter(wishlist_users__user=request.user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'core/wishlist.html', context)


@login_required
@require_POST
def purchase_item(request):
    """Handle purchase of a market item."""
    item_id = request.POST.get('item_id')
    if not item_id:
        messages.error(request, "No item specified.")
        return redirect('core:store')
    
    try:
        item = MarketItem.objects.get(id=item_id)
        
        # Simple mock purchase logic
        if item.is_available:
            # In a real app, we would check currency, credits, or other requirements
            # and handle the actual transaction
            messages.success(request, f"Successfully purchased {item.name}!")
            
            # For educational economic models, different logic would apply
            if item.economic_layer == 'inner':
                messages.info(request, "This purchase supports the Republic economic model.")
            elif item.economic_layer == 'middle':
                messages.info(request, "This purchase supports the Laws economic model.")
            else:
                messages.info(request, "This purchase supports the Port City economic model.")
        else:
            messages.error(request, f"{item.name} is not available for purchase.")
            
    except MarketItem.DoesNotExist:
        messages.error(request, "Item not found.")
    
    # Redirect back to the store or to a receipt page
    return redirect('core:store')


class NotificationsView(LoginRequiredMixin, TemplateView):
    """View for displaying user notifications."""
    template_name = 'core/notifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Mock notification data - in a real implementation, this would come from a Notification model
        notifications = [
            {
                'id': 1,
                'type': 'achievement',
                'title': 'New Achievement!',
                'message': 'You have earned the "Early Bird" achievement for logging in 5 days in a row.',
                'timestamp': timezone.now() - timezone.timedelta(hours=2),
                'is_read': False
            },
            {
                'id': 2,
                'type': 'zone',
                'title': 'New Zone Discovered',
                'message': 'You have discovered the "Library" zone. Explore it to gain knowledge resources!',
                'timestamp': timezone.now() - timezone.timedelta(days=1),
                'is_read': True
            },
            {
                'id': 3,
                'type': 'experience',
                'title': 'Experience Completed',
                'message': 'You have completed the "Campus Tour" experience. +20 XP earned!',
                'timestamp': timezone.now() - timezone.timedelta(days=2),
                'is_read': True
            },
            {
                'id': 4,
                'type': 'social',
                'title': 'Friend Request',
                'message': 'User JaneDoe wants to connect with you.',
                'timestamp': timezone.now() - timezone.timedelta(days=3),
                'is_read': False
            },
            {
                'id': 5,
                'type': 'art',
                'title': 'New Art Available',
                'message': 'The art "Photography" is now available for you to learn.',
                'timestamp': timezone.now() - timezone.timedelta(days=4),
                'is_read': False
            }
        ]
        
        unread_count = sum(1 for n in notifications if not n['is_read'])
        
        context.update({
            'notifications': notifications,
            'unread_count': unread_count
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests to mark notifications as read."""
        notification_id = request.POST.get('notification_id')
        mark_all_read = request.POST.get('mark_all_read')
        
        if mark_all_read:
            # Logic to mark all notifications as read would go here
            messages.success(request, "All notifications marked as read.")
        elif notification_id:
            # Logic to mark a specific notification as read would go here
            messages.success(request, "Notification marked as read.")
        
        return redirect('core:notifications')


class ZoneView(LoginRequiredMixin, TemplateView):
    """View for displaying zone information and activities."""
    template_name = 'core/zone.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_profile = PlayerProfile.objects.get(user=self.request.user)
        
        # This is a placeholder until full Zone models are implemented
        # In a real implementation, we would get the current zone from the player's location
        zone_id = self.request.GET.get('zone_id', None)
        
        # Mock zone data - in a real implementation, this would come from the database
        zone = {
            'id': zone_id or 'campus-center',
            'name': 'Campus Center',
            'description': 'The heart of university life, where students gather for socializing and activities.',
            'level': 1,
            'population': 120,
            'resources': ['knowledge', 'social', 'creativity'],
            'activities': [
                {'name': 'Study Group', 'xp': 50, 'time': '30 min'},
                {'name': 'Campus Tour', 'xp': 20, 'time': '15 min'},
                {'name': 'Community Service', 'xp': 100, 'time': '1 hour'}
            ],
            'latitude': player_profile.latitude or 40.7128,
            'longitude': player_profile.longitude or -74.0060,
        }
        
        context.update({
            'player_profile': player_profile,
            'zone': zone,
            'nearby_players': 5,  # Placeholder
        })
        
        return context


class VirtuesView(LoginRequiredMixin, TemplateView):
    """View for displaying player virtues and character development information."""
    template_name = 'core/virtues.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_profile = PlayerProfile.objects.get(user=self.request.user)
        
        # Mock data for happiness and subcategories
        happiness_score = 78
        
        # Good category with 4 virtues
        good_score = 70
        good_virtues = [
            {
                'id': 'wisdom',
                'name': 'Wisdom',
                'description': 'The quality of having experience, knowledge, and good judgment.',
                'level': 3,
                'progress': 75,
                'icon': 'brain',
            },
            {
                'id': 'courage',
                'name': 'Courage',
                'description': 'The ability to face fear and danger with confidence.',
                'level': 4,
                'progress': 80,
                'icon': 'fist-raised',
            },
            {
                'id': 'temperance',
                'name': 'Temperance',
                'description': 'Moderation or self-restraint in action, statement, etc.',
                'level': 3,
                'progress': 65,
                'icon': 'balance-scale',
            },
            {
                'id': 'justice',
                'name': 'Justice',
                'description': 'The quality of being fair and reasonable.',
                'level': 2,
                'progress': 60,
                'icon': 'gavel',
            }
        ]
        
        # Fortune category with 4 attributes
        fortune_score = 75
        fortune_virtues = [
            {
                'id': 'strength',
                'name': 'Strength',
                'description': 'Physical power and energy.',
                'level': 4,
                'progress': 78,
                'icon': 'dumbbell',
            },
            {
                'id': 'health',
                'name': 'Health',
                'description': 'The state of being free from illness or injury.',
                'level': 3,
                'progress': 72,
                'icon': 'heartbeat',
            },
            {
                'id': 'beauty',
                'name': 'Beauty',
                'description': 'A combination of qualities that pleases the aesthetic senses.',
                'level': 4,
                'progress': 85,
                'icon': 'paint-brush',
            },
            {
                'id': 'endurance',
                'name': 'Endurance',
                'description': 'The ability to endure difficult conditions.',
                'level': 3,
                'progress': 65,
                'icon': 'running',
            }
        ]
        
        # Mixed category with 4 attributes
        mixed_score = 68
        mixed_virtues = [
            {
                'id': 'friendship',
                'name': 'Friendship',
                'description': 'The state of being friends.',
                'level': 3,
                'progress': 70,
                'icon': 'users',
            },
            {
                'id': 'resources',
                'name': 'Resources',
                'description': 'A stock or supply of materials or assets.',
                'level': 3,
                'progress': 65,
                'icon': 'gem',
            },
            {
                'id': 'honors',
                'name': 'Honors',
                'description': 'High respect or distinction.',
                'level': 3,
                'progress': 72,
                'icon': 'trophy',
            },
            {
                'id': 'glories',
                'name': 'Glories',
                'description': 'High renown or honor won by notable achievements.',
                'level': 3,
                'progress': 65,
                'icon': 'star',
            }
        ]
        
        # Example of detailed breakdown for Wisdom
        wisdom_details = [
            {'name': 'Knowledge', 'progress': 80},
            {'name': 'Reading', 'progress': 70},
            {'name': 'Reflection', 'progress': 75},
            # Additional details could be added here
        ]
        
        context.update({
            'player_profile': player_profile,
            'happiness_score': happiness_score,
            'good_score': good_score,
            'good_virtues': good_virtues,
            'fortune_score': fortune_score, 
            'fortune_virtues': fortune_virtues,
            'mixed_score': mixed_score,
            'mixed_virtues': mixed_virtues,
            'wisdom_details': wisdom_details,
            'active_tab': 'virtues'
        })
        
        return context


class MarketItemDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a market item."""
    template_name = 'core/market_item_detail.html'
    context_object_name = 'item'
    
    def get_object(self, queryset=None):
        # For now, return a mock item
        item_id = self.kwargs.get('item_id')
        # Mock data - in a real app, fetch from database
        return {
            'id': item_id,
            'name': f'Item {item_id}',
            'description': 'A detailed description of this market item.',
            'price': 100,
            'currency': 'Credits',
            'category': 'Equipment',
            'rating': 4.5,
            'available': True,
            'seller': 'Game Store',
            'image_url': '/static/images/placeholder.png'
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_items'] = [
            {'id': i, 'name': f'Related Item {i}', 'price': 50 + i * 10}
            for i in range(1, 4)
        ]
        return context


class PublicStoreView(TemplateView):
    """Public version of the Store page for non-logged-in users."""
    template_name = 'core/store.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items_count'] = MarketItem.objects.count()
        context['filtered_count'] = context['total_items_count']
        context['wishlist_count'] = 0
        context['recent_transactions'] = []
        return context


class AboutView(TemplateView):
    """About page for AION - The New Academy."""
    template_name = 'core/about.html'


class AboutView(TemplateView):
    """About page for AION - The New Academy."""
    template_name = 'core/about.html'

# AtlantisMapView removed since MapView now uses the Atlantis map template 