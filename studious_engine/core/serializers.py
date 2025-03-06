from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    PlayerProfile, 
    PlayerHappiness, 
    UserPreferences, 
    UserLocation,
    MarketItem,
    Wishlist
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']

class PlayerHappinessSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerHappiness model."""
    class Meta:
        model = PlayerHappiness
        fields = [
            'id', 'wisdom', 'courage', 'temperance', 'justice',
            'strength', 'health', 'beauty', 'endurance',
            'happiness', 'good_score', 'prosperity_score',
            'last_calculated'
        ]
        read_only_fields = [
            'id', 'happiness', 'good_score', 'prosperity_score',
            'last_calculated'
        ]

class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for the UserPreferences model."""
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'interface_settings', 'notification_preferences',
            'privacy_settings', 'ai_guide_settings',
            'language_preference', 'accessibility_options'
        ]
        read_only_fields = ['id']

class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for the UserLocation model."""
    class Meta:
        model = UserLocation
        fields = [
            'id', 'latitude', 'longitude', 'current_zone_id',
            'previous_zones', 'accuracy_meters', 'device_id',
            'last_updated'
        ]
        read_only_fields = ['id', 'previous_zones', 'last_updated']

class PlayerProfileSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerProfile model."""
    user = UserSerializer(read_only=True)
    happiness_data = PlayerHappinessSerializer(source='happiness', read_only=True)
    economic_layer_display = serializers.CharField(source='get_economic_layer_display', read_only=True)
    
    class Meta:
        model = PlayerProfile
        fields = [
            'id', 'user', 'rank', 'experience_points',
            'economic_layer', 'economic_layer_display',
            'avatar', 'title', 'bio', 
            'tutorial_progress', 'device_settings',
            'last_active', 'created_at', 'updated_at',
            'happiness_data', 'level'
        ]
        read_only_fields = [
            'id', 'user', 'last_active', 'created_at', 
            'updated_at', 'happiness_data', 'level',
            'economic_layer_display'
        ]

class MarketItemSerializer(serializers.ModelSerializer):
    """Serializer for the MarketItem model."""
    economic_layer_display = serializers.CharField(source='get_economic_layer_display', read_only=True)
    price_type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    seller_type_display = serializers.CharField(source='get_seller_type_display', read_only=True)
    
    class Meta:
        model = MarketItem
        fields = [
            'id', 'name', 'description', 'image', 
            'economic_layer', 'economic_layer_display',
            'price', 'price_type', 'price_type_display',
            'category', 'category_display',
            'is_available', 'quantity', 'available_until',
            'min_rank_required', 'created_at', 'updated_at',
            'is_featured', 'recommendation_score',
            'seller_id', 'seller_type', 'seller_type_display',
            'reference_id'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'economic_layer_display', 'price_type_display',
            'category_display', 'seller_type_display'
        ]

class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for the Wishlist model."""
    item_details = MarketItemSerializer(source='item', read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'item', 'item_details', 'added_at']
        read_only_fields = ['id', 'added_at'] 