from rest_framework import serializers
from experiences.models import Experience, PlayerExperience, Power, PlayerPower

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class PowerSerializer(serializers.ModelSerializer):
    """Serializer for the Power model."""
    power_type_display = serializers.CharField(source='get_power_type_display', read_only=True)
    
    class Meta:
        model = Power
        fields = [
            'id', 'name', 'description', 'power_type', 'power_type_display',
            'rarity', 'complexity', 'sector', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlayerPowerSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerPower model."""
    power_details = PowerSerializer(source='power', read_only=True)
    
    class Meta:
        model = PlayerPower
        fields = [
            'id', 'player', 'power', 'power_details', 'level',
            'experience', 'acquired_at', 'last_used_at'
        ]
        read_only_fields = ['id', 'acquired_at']

class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for the Experience model."""
    experience_type_display = serializers.CharField(source='get_experience_type_display', read_only=True)
    matrix_position_display = serializers.CharField(source='get_matrix_position_display', read_only=True)
    art_type_display = serializers.CharField(source='get_art_type_display', read_only=True)
    good_type_display = serializers.CharField(source='get_good_type_display', read_only=True)
    
    class Meta:
        model = Experience
        fields = [
            'id', 'name', 'description', 
            'experience_type', 'experience_type_display',
            'matrix_position', 'matrix_position_display',
            'art_type', 'art_type_display',
            'good_type', 'good_type_display',
            'latitude', 'longitude',
            'difficulty', 'duration_minutes',
            'happiness_reward', 'experience_reward',
            'definition', 'end', 'parts', 'matter', 'instrument',
            'is_active', 'minimum_rank', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlayerExperienceSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerExperience model."""
    experience_details = ExperienceSerializer(source='experience', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PlayerExperience
        fields = [
            'id', 'player', 'experience', 'experience_details',
            'status', 'status_display', 'progress', 'reflection_notes',
            'resources_committed', 'happiness_gained', 'experience_gained',
            'started_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'updated_at'] 