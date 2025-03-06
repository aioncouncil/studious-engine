from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import Http404
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

from core.models import (
    PlayerProfile, PlayerHappiness, UserPreferences, 
    UserLocation, MarketItem, Wishlist
)
from core.serializers import (
    PlayerProfileSerializer, PlayerHappinessSerializer,
    UserPreferencesSerializer, UserLocationSerializer,
    MarketItemSerializer, WishlistSerializer
)
from core.services.user_service import UserService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()


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
        """Get detailed profile with related data."""
        profile = self.get_object()
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
        
        # Extract virtue updates from request data
        virtue_updates = {}
        for virtue in ['wisdom', 'courage', 'temperance', 'justice',
                      'strength', 'health', 'beauty', 'endurance']:
            if virtue in request.data:
                try:
                    value = float(request.data[virtue])
                    # Clamp values to 0-100
                    value = max(0, min(100, value))
                    virtue_updates[virtue] = value
                except (ValueError, TypeError):
                    return Response(
                        {"error": f"Invalid value for {virtue}. Must be a number between 0-100."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        if not virtue_updates:
            return Response(
                {"error": "No virtue updates provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the virtues using the service
        updated_happiness = UserService.update_happiness(profile, **virtue_updates)
        
        serializer = PlayerHappinessSerializer(updated_happiness)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'patch'])
    def preferences(self, request, pk=None):
        """Get or update user preferences."""
        profile = self.get_object()
        
        # Handle GET request
        if request.method == 'GET':
            serializer = UserPreferencesSerializer(profile.preferences)
            return Response(serializer.data)
        
        # Handle PATCH request
        serializer = UserPreferencesSerializer(profile.preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'])
    def location(self, request, pk=None):
        """Get or update user location."""
        profile = self.get_object()
        
        # Handle GET request
        if request.method == 'GET':
            try:
                serializer = UserLocationSerializer(profile.location)
                return Response(serializer.data)
            except UserLocation.DoesNotExist:
                return Response(
                    {"error": "Location not set"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Handle POST request
        if 'latitude' not in request.data or 'longitude' not in request.data:
            return Response(
                {"error": "Latitude and longitude are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            latitude = float(request.data['latitude'])
            longitude = float(request.data['longitude'])
            accuracy = float(request.data.get('accuracy_meters', 0))
            device_id = request.data.get('device_id', '')
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid coordinates."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        location = UserService.update_location(profile, latitude, longitude, accuracy, device_id)
        serializer = UserLocationSerializer(location)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def economic_permissions(self, request, pk=None):
        """Get permissions based on economic layer."""
        profile = self.get_object()
        permissions = UserService.get_economic_layer_permissions(profile)
        return Response(permissions)
    
    @action(detail=True, methods=['get'])
    def recommended_experiences(self, request, pk=None):
        """Get experiences recommended for this player."""
        profile = self.get_object()
        count = request.query_params.get('count', 3)
        try:
            count = int(count)
        except ValueError:
            count = 3
        
        recommendations = UserService.recommend_experiences(profile, count=count)
        return Response(recommendations)


class MarketItemViewSet(viewsets.ModelViewSet):
    """API endpoint for market items."""
    queryset = MarketItem.objects.all()
    serializer_class = MarketItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter market items based on query parameters and user's rank/economic layer."""
        queryset = MarketItem.objects.all()
        
        # Get user's profile for economic layer and rank filtering
        try:
            profile = PlayerProfile.objects.get(user=self.request.user)
            user_rank = profile.rank
            user_economic_layer = profile.economic_layer
        except PlayerProfile.DoesNotExist:
            user_rank = 1
            user_economic_layer = 'port'  # Default to outer economic layer
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', 'true').lower() == 'true'
        if available_only:
            queryset = queryset.filter(is_available=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by economic layer
        economic_layer = self.request.query_params.get('economic_layer')
        if economic_layer:
            queryset = queryset.filter(economic_layer=economic_layer)
        else:
            # Apply economic layer filtering based on user's layer
            if user_economic_layer == 'port':
                queryset = queryset.filter(economic_layer='outer')
            elif user_economic_layer == 'laws':
                queryset = queryset.filter(economic_layer__in=['outer', 'middle'])
            # 'republic' layer users can see all layers
        
        # Filter by rank
        queryset = queryset.filter(min_rank_required__lte=user_rank)
        
        # Featured items
        featured_only = self.request.query_params.get('featured_only', 'false').lower() == 'true'
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        """Add an item to the user's wishlist."""
        item = self.get_object()
        user = request.user
        
        # Check if already in wishlist
        wishlist_entry = Wishlist.objects.filter(user=user, item=item).first()
        if wishlist_entry:
            return Response(
                {"message": "Item already in wishlist."},
                status=status.HTTP_200_OK
            )
        
        # Add to wishlist
        wishlist = Wishlist.objects.create(user=user, item=item)
        serializer = WishlistSerializer(wishlist)
        return Response(
            {"message": "Item added to wishlist.", "wishlist": serializer.data},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request, pk=None):
        """Remove an item from the user's wishlist."""
        item = self.get_object()
        user = request.user
        
        # Check if in wishlist
        wishlist_entry = Wishlist.objects.filter(user=user, item=item).first()
        if not wishlist_entry:
            return Response(
                {"message": "Item not in wishlist."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove from wishlist
        wishlist_entry.delete()
        return Response(
            {"message": "Item removed from wishlist."},
            status=status.HTTP_200_OK
        )


class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for user's wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to only show current user's wishlist."""
        return Wishlist.objects.filter(user=self.request.user) 