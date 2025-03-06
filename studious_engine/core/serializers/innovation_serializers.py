from rest_framework import serializers
from innovations.models import Innovation, InnovationContribution, TechTreeNode
from .zone_serializers import SectorSerializer, ZoneSerializer

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class TechTreeNodeSerializer(serializers.ModelSerializer):
    """Serializer for the TechTreeNode model."""
    sector_details = SectorSerializer(source='sector', read_only=True)
    unlocked_by_innovation_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TechTreeNode
        fields = [
            'id', 'name', 'description', 
            'sector', 'sector_details', 'level',
            'prerequisites', 'unlocked_experiences', 'unlocked_powers',
            'is_unlocked', 'unlocked_at', 'unlocked_by_innovation',
            'unlocked_by_innovation_details',
            'icon', 'position_x', 'position_y',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_unlocked_by_innovation_details(self, obj):
        """Get the innovation details that unlocked this tech tree node."""
        if obj.unlocked_by_innovation:
            return {
                'id': obj.unlocked_by_innovation.id,
                'name': obj.unlocked_by_innovation.name,
                'description': obj.unlocked_by_innovation.description
            }
        return None

class InnovationSerializer(serializers.ModelSerializer):
    """Serializer for the Innovation model."""
    sector_details = SectorSerializer(source='sector', read_only=True)
    zones_details = ZoneSerializer(source='zones', many=True, read_only=True)
    current_stage_display = serializers.CharField(source='get_current_stage_display', read_only=True)
    unlocked_tech = TechTreeNodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Innovation
        fields = [
            'id', 'name', 'description',
            'sector', 'sector_details', 'zones', 'zones_details',
            'current_stage', 'current_stage_display', 'progress',
            'order_components', 'order_metrics',
            'arrangement_ground_plan', 'arrangement_elevation', 'arrangement_perspective',
            'eurythmy_components',
            'symmetry_standard', 'symmetry_relations',
            'propriety_principles', 'propriety_justification',
            'economy_resources', 'economy_implementation',
            'is_approved', 'implementation_date',
            'expected_impact', 'actual_impact',
            'affects_tech_tree', 'tech_tree_node',
            'unlocked_tech', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class InnovationContributionSerializer(serializers.ModelSerializer):
    """Serializer for the InnovationContribution model."""
    innovation_details = InnovationSerializer(source='innovation', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    
    class Meta:
        model = InnovationContribution
        fields = [
            'id', 'player', 'innovation', 'innovation_details',
            'stage', 'stage_display', 'contribution_description',
            'impact_level', 'experience_reward', 'happiness_reward',
            'contributed_at'
        ]
        read_only_fields = ['id', 'contributed_at'] 