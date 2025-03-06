from rest_framework import serializers
from core.models import PlayerProfile, PlayerHappiness, UserPreferences, UserLocation
from studious_engine.users.api.serializers import UserSerializer

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class PlayerHappinessSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerHappiness model."""
    
    class Meta:
        model = PlayerHappiness
        fields = [
            'id', 'profile', 'happiness_score', 'energy',
            'cognitive_state', 'motivation', 'recent_activities',
            'tracked_emotions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'profile', 'created_at', 'updated_at']


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
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for the UserPreferences model."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'user', 'notification_preferences', 'privacy_settings',
            'ui_preferences', 'learning_preferences', 'analytics_sharing',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for the UserLocation model."""
    
    class Meta:
        model = UserLocation
        fields = [
            'id', 'user', 'latitude', 'longitude', 'last_known_location',
            'previous_zones', 'last_updated'
        ]
        read_only_fields = ['id', 'previous_zones', 'last_updated'] 