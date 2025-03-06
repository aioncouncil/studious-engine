from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import PlayerProfile, PlayerHappiness, UserPreferences, UserLocation, MarketItem, Wishlist
from .services.user_service import UserService

# Serializers will be imported from serializers.py
from .serializers import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    PlayerProfileSerializer, 
    PlayerHappinessSerializer,
    UserPreferencesSerializer, 
    UserLocationSerializer,
    MarketItemSerializer,
    WishlistSerializer
)

class PlayerProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for player profiles."""
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to only show own profile unless staff."""
        user = self.request.user
        if user.is_staff:
            return PlayerProfile.objects.all()
        return PlayerProfile.objects.filter(user=user)
    
    def retrieve(self, request, pk=None):
        """Get player profile with permissions check."""
        user = request.user
        queryset = self.get_queryset()
        profile = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def happiness(self, request, pk=None):
        """Get player's happiness metrics."""
        profile = self.get_object()
        happiness = profile.happiness
        serializer = PlayerHappinessSerializer(happiness)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_virtues(self, request, pk=None):
        """Update player's virtue metrics."""
        profile = self.get_object()
        
        # Extract virtue values from request data
        virtue_updates = {}
        valid_virtues = [
            'wisdom', 'courage', 'temperance', 'justice',
            'strength', 'health', 'beauty', 'endurance'
        ]
        
        for virtue in valid_virtues:
            if virtue in request.data:
                try:
                    value = float(request.data[virtue])
                    virtue_updates[virtue] = value
                except (ValueError, TypeError):
                    return Response(
                        {f"error": f"Invalid value for {virtue}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        if not virtue_updates:
            return Response(
                {"error": "No valid virtue updates provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use service to update happiness
        happiness = UserService.update_happiness(profile, **virtue_updates)
        serializer = PlayerHappinessSerializer(happiness)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'patch'])
    def preferences(self, request, pk=None):
        """Get or update player preferences."""
        profile = self.get_object()
        preferences = profile.preferences
        
        if request.method == 'PATCH':
            serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def location(self, request, pk=None):
        """Get or update player location."""
        profile = self.get_object()
        location = profile.location
        
        if request.method == 'POST':
            serializer = UserLocationSerializer(location, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Use service to update location
            UserService.update_location(
                profile,
                serializer.validated_data.get('latitude'),
                serializer.validated_data.get('longitude'),
                serializer.validated_data.get('accuracy_meters'),
                serializer.validated_data.get('device_id')
            )
            
            # Refresh location data after update
            location.refresh_from_db()
            serializer = UserLocationSerializer(location)
            return Response(serializer.data)
            
        serializer = UserLocationSerializer(location)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def economic_permissions(self, request, pk=None):
        """Get economic layer permissions for the user."""
        profile = self.get_object()
        permissions = UserService.get_economic_layer_permissions(profile)
        return Response(permissions)
    
    @action(detail=True, methods=['get'])
    def recommended_experiences(self, request, pk=None):
        """Get recommended experiences for the user."""
        profile = self.get_object()
        count = int(request.query_params.get('count', 3))
        
        # Get recommendations from service
        recommendations = UserService.recommend_experiences(profile, count)
        return Response(recommendations)

class MarketItemViewSet(viewsets.ModelViewSet):
    """API endpoint for market items."""
    queryset = MarketItem.objects.all()
    serializer_class = MarketItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter market items based on user's economic layer and rank."""
        queryset = MarketItem.objects.filter(is_available=True)
        
        # Apply filters from query parameters
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
            
        layer = self.request.query_params.get('layer', None)
        if layer:
            queryset = queryset.filter(economic_layer=layer)
            
        # Get user profile
        try:
            profile = self.request.user.profile
            
            # Filter by minimum rank
            queryset = queryset.filter(min_rank_required__lte=profile.rank)
            
            # If not staff, filter by economic layer permission
            if not self.request.user.is_staff:
                # Port city users can only see outer layer
                if profile.economic_layer == 'port':
                    queryset = queryset.filter(economic_layer='outer')
                # Laws model users can see outer and middle layers
                elif profile.economic_layer == 'laws':
                    queryset = queryset.filter(economic_layer__in=['outer', 'middle'])
                # Republic model users can see all layers
        except PlayerProfile.DoesNotExist:
            # If no profile, only show outer layer items with rank 1
            queryset = queryset.filter(economic_layer='outer', min_rank_required=1)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        """Add an item to user's wishlist."""
        item = self.get_object()
        user = request.user
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=user, item=item).exists():
            return Response(
                {"message": "Item already in wishlist"}, 
                status=status.HTTP_200_OK
            )
        
        # Add to wishlist
        wishlist_item = Wishlist.objects.create(user=user, item=item)
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request, pk=None):
        """Remove an item from user's wishlist."""
        item = self.get_object()
        user = request.user
        
        try:
            wishlist_item = Wishlist.objects.get(user=user, item=item)
            wishlist_item.delete()
            return Response(
                {"message": "Item removed from wishlist"},
                status=status.HTTP_200_OK
            )
        except Wishlist.DoesNotExist:
            return Response(
                {"message": "Item not in wishlist"},
                status=status.HTTP_404_NOT_FOUND
            )

class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for user's wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only show current user's wishlist."""
        return Wishlist.objects.filter(user=self.request.user) 