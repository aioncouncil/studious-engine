from rest_framework import serializers
from core.models import Art, ArtParts, ArtStage, ArtTaxonomy

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ArtTaxonomySerializer(serializers.ModelSerializer):
    """Serializer for the ArtTaxonomy model."""
    
    class Meta:
        model = ArtTaxonomy
        fields = ['id', 'name', 'description', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ArtPartSerializer(serializers.ModelSerializer):
    """Serializer for the ArtParts model."""
    
    practice_method_display = serializers.CharField(source='get_practice_method_display', read_only=True)
    validation_method_display = serializers.CharField(source='get_validation_method_display', read_only=True)
    
    class Meta:
        model = ArtParts
        fields = [
            'id', 'art', 'name', 'description', 'practice_method', 'practice_method_display',
            'validation_method', 'validation_method_display', 'estimated_hours',
            'difficulty_level', 'order_index', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ArtStageSerializer(serializers.ModelSerializer):
    """Serializer for the ArtStage model."""
    
    class Meta:
        model = ArtStage
        fields = [
            'id', 'art', 'name', 'description', 'mastery_threshold',
            'order_index', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ArtSerializer(serializers.ModelSerializer):
    """Serializer for the Art model."""
    
    taxonomy = ArtTaxonomySerializer(read_only=True)
    taxonomy_id = serializers.PrimaryKeyRelatedField(
        queryset=ArtTaxonomy.objects.all(),
        source='taxonomy',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Art
        fields = [
            'id', 'name', 'description', 'taxonomy', 'taxonomy_id',
            'difficulty_level', 'virtue_benefits', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ArtDetailSerializer(ArtSerializer):
    """Detailed serializer for the Art model including related parts and stages."""
    
    parts = ArtPartSerializer(many=True, read_only=True, source='artparts_set')
    stages = ArtStageSerializer(many=True, read_only=True, source='artstage_set')
    
    class Meta(ArtSerializer.Meta):
        fields = ArtSerializer.Meta.fields + ['parts', 'stages'] 