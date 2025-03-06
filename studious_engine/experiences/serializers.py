from rest_framework import serializers
from .models import (
    Power, PlayerPower, Experience, PlayerExperience,
    ExperienceInstance, ExperienceParticipation
)
from core.models import PlayerProfile as Player
from core.serializers import PlayerProfileSerializer as PlayerSerializer

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class PowerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Power
        fields = ['id', 'name', 'power_type', 'rarity', 'complexity', 'sector', 'is_public']


class PowerDetailSerializer(serializers.ModelSerializer):
    prerequisites = PowerListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Power
        fields = [
            'id', 'name', 'description', 'power_type', 'rarity', 'complexity', 
            'sector', 'is_public', 'prerequisites', 'created_at', 'updated_at'
        ]


class PlayerPowerSerializer(serializers.ModelSerializer):
    power = PowerListSerializer(read_only=True)
    power_id = serializers.PrimaryKeyRelatedField(
        queryset=Power.objects.all(), 
        write_only=True,
        source='power'
    )
    
    class Meta:
        model = PlayerPower
        fields = [
            'id', 'player', 'power', 'power_id', 'level', 'experience',
            'acquired_at', 'last_used_at'
        ]
        read_only_fields = ['acquired_at', 'last_used_at']


class ExperienceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id', 'name', 'experience_type', 'matrix_position',
            'difficulty', 'duration_minutes', 'is_active'
        ]


class ExperienceDetailSerializer(serializers.ModelSerializer):
    required_powers = PowerListSerializer(many=True, read_only=True)
    prerequisite_experiences = ExperienceListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Experience
        fields = [
            'id', 'name', 'description', 'experience_type', 'matrix_position',
            'art_type', 'good_type', 'difficulty', 'duration_minutes',
            'happiness_reward', 'experience_reward', 'latitude', 'longitude',
            'required_powers', 'associated_zones', 'prerequisite_experiences',
            'definition', 'end', 'parts', 'matter', 'instrument',
            'minimum_rank', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]


class PlayerExperienceSerializer(serializers.ModelSerializer):
    experience = ExperienceListSerializer(read_only=True)
    experience_id = serializers.PrimaryKeyRelatedField(
        queryset=Experience.objects.all(),
        write_only=True,
        source='experience'
    )
    
    class Meta:
        model = PlayerExperience
        fields = [
            'id', 'player', 'experience', 'experience_id', 'status', 'progress',
            'reflection_notes', 'resources_committed', 'happiness_gained',
            'experience_gained', 'started_at', 'completed_at'
        ]
        read_only_fields = ['started_at', 'completed_at']


class ExperienceInstanceListSerializer(serializers.ModelSerializer):
    experience_name = serializers.CharField(source='experience.name', read_only=True)
    host_name = serializers.CharField(source='host.user.username', read_only=True)
    
    class Meta:
        model = ExperienceInstance
        fields = [
            'id', 'name', 'experience', 'experience_name', 'host', 'host_name',
            'zone', 'start_time', 'end_time', 'status', 'current_participants',
            'capacity', 'is_public'
        ]


class ExperienceInstanceDetailSerializer(serializers.ModelSerializer):
    experience = ExperienceListSerializer(read_only=True)
    experience_id = serializers.PrimaryKeyRelatedField(
        queryset=Experience.objects.all(),
        write_only=True,
        source='experience'
    )
    host = PlayerSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        write_only=True,
        source='host'
    )
    is_active = serializers.BooleanField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ExperienceInstance
        fields = [
            'id', 'experience', 'experience_id', 'name', 'host', 'host_id',
            'zone', 'start_time', 'end_time', 'frequency', 'recurrence_rule',
            'status', 'capacity', 'current_participants', 'is_public',
            'location_description', 'meeting_point', 'current_matrix_phase',
            'matrix_flow_data', 'resources_provided', 'outcomes',
            'is_active', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_participants', 'created_at', 'updated_at']


class ExperienceParticipationListSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.user.username', read_only=True)
    instance_name = serializers.CharField(source='instance.name', read_only=True)
    
    class Meta:
        model = ExperienceParticipation
        fields = [
            'id', 'instance', 'instance_name', 'player', 'player_name',
            'status', 'joined_at', 'completed_at', 'satisfaction_rating'
        ]


class ExperienceParticipationDetailSerializer(serializers.ModelSerializer):
    instance = ExperienceInstanceListSerializer(read_only=True)
    instance_id = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceInstance.objects.all(),
        write_only=True,
        source='instance'
    )
    player = PlayerSerializer(read_only=True)
    player_id = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        write_only=True,
        source='player'
    )
    
    class Meta:
        model = ExperienceParticipation
        fields = [
            'id', 'instance', 'instance_id', 'player', 'player_id',
            'status', 'joined_at', 'completed_at', 'withdrawn_at',
            'contributions', 'personal_outcomes', 'feedback',
            'satisfaction_rating', 'happiness_gained', 'experience_gained',
            'resources_gained', 'individual_flow_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['joined_at', 'completed_at', 'withdrawn_at', 'created_at', 'updated_at'] 