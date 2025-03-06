from rest_framework import serializers
from zones.models import Sector, Zone, ZoneHappiness, PlayerZoneContribution

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class SectorSerializer(serializers.ModelSerializer):
    """Serializer for the Sector model."""
    
    class Meta:
        model = Sector
        fields = [
            'id', 'number', 'name', 'description',
            'is_governing', 'governing_start_date', 'governing_end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ZoneHappinessSerializer(serializers.ModelSerializer):
    """Serializer for the ZoneHappiness model."""
    
    class Meta:
        model = ZoneHappiness
        fields = [
            'id', 'zone', 'wisdom', 'courage', 'temperance', 'justice',
            'strength', 'health', 'beauty', 'endurance',
            'happiness', 'good_score', 'prosperity_score',
            'last_calculated'
        ]
        read_only_fields = ['id', 'last_calculated']

class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for the Zone model."""
    sector_details = SectorSerializer(source='sector', read_only=True)
    area_display = serializers.CharField(source='get_area_display', read_only=True)
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    happiness_data = ZoneHappinessSerializer(source='happiness', read_only=True)
    
    class Meta:
        model = Zone
        fields = [
            'id', 'sector', 'sector_details', 'zone_number', 'zone_type',
            'area', 'area_display', 'rank', 'rank_display',
            'description', 'city', 'country',
            'city_latitude', 'city_longitude',
            'country_latitude', 'country_longitude',
            'is_active', 'created_at', 'updated_at',
            'happiness_data'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlayerZoneContributionSerializer(serializers.ModelSerializer):
    """Serializer for the PlayerZoneContribution model."""
    zone_details = ZoneSerializer(source='zone', read_only=True)
    
    class Meta:
        model = PlayerZoneContribution
        fields = [
            'id', 'player', 'zone', 'zone_details',
            'think_tank_contributions', 'production_tank_contributions',
            'overall_influence', 'is_zone_leader',
            'leadership_start_date', 'leadership_end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 