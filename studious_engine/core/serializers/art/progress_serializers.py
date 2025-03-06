from rest_framework import serializers
from core.models import (
    ArtMastery, 
    UserArtStageProgress, 
    UserTechTreeProgress,
    TechTree
)
from .art_serializers import ArtSerializer, ArtPartSerializer, ArtStageSerializer

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ArtMasterySerializer(serializers.ModelSerializer):
    """Serializer for the ArtMastery model."""
    
    art = ArtSerializer(read_only=True)
    current_part = ArtPartSerializer(read_only=True)
    
    class Meta:
        model = ArtMastery
        fields = [
            'id', 'user', 'art', 'mastery_level', 'discovery_date',
            'last_practice_date', 'practice_streak', 'practice_count',
            'current_part', 'completed_parts', 'practice_history'
        ]
        read_only_fields = ['id', 'user', 'art', 'discovery_date']
    
    def to_representation(self, instance):
        """Custom representation to include additional data."""
        ret = super().to_representation(instance)
        
        # Include total parts count
        if instance.art:
            ret['total_parts'] = instance.art.artparts_set.count()
            ret['completed_parts_count'] = len(instance.completed_parts or [])
            
            # Calculate percentage complete
            if ret['total_parts'] > 0:
                ret['percent_complete'] = (ret['completed_parts_count'] / ret['total_parts']) * 100
            else:
                ret['percent_complete'] = 0
        
        return ret


class UserArtStageProgressSerializer(serializers.ModelSerializer):
    """Serializer for the UserArtStageProgress model."""
    
    art_stage = ArtStageSerializer(read_only=True)
    
    class Meta:
        model = UserArtStageProgress
        fields = [
            'id', 'user', 'art_stage', 'unlocked', 'unlock_date',
            'completed', 'completion_date'
        ]
        read_only_fields = ['id', 'user', 'art_stage', 'unlock_date', 'completion_date']


class TechTreeSerializer(serializers.ModelSerializer):
    """Serializer for the TechTree model."""
    
    arts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TechTree
        fields = [
            'id', 'name', 'description', 'achievement_bonus',
            'created_at', 'updated_at', 'arts_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_arts_count(self, obj):
        """Get the number of arts in this tech tree."""
        return obj.arts.count()


class UserTechTreeProgressSerializer(serializers.ModelSerializer):
    """Serializer for the UserTechTreeProgress model."""
    
    tech_tree = TechTreeSerializer(read_only=True)
    
    class Meta:
        model = UserTechTreeProgress
        fields = [
            'id', 'user', 'tech_tree', 'progress_percentage', 'is_unlocked', 'unlocked_date'
        ]
        read_only_fields = ['id', 'user', 'tech_tree', 'unlocked_date']


class PracticeSessionSerializer(serializers.Serializer):
    """Serializer for logging practice sessions."""
    
    art_id = serializers.IntegerField(required=True)
    part_id = serializers.IntegerField(required=False, allow_null=True)
    duration_minutes = serializers.IntegerField(required=True, min_value=1, max_value=480)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, data):
        """Validate that the art and part exist."""
        from core.models import Art, ArtParts
        
        try:
            art = Art.objects.get(id=data['art_id'])
        except Art.DoesNotExist:
            raise serializers.ValidationError({"art_id": "Art with this ID does not exist."})
        
        if 'part_id' in data and data['part_id']:
            try:
                part = ArtParts.objects.get(id=data['part_id'], art=art)
            except ArtParts.DoesNotExist:
                raise serializers.ValidationError({"part_id": "Part with this ID does not exist for this art."})
        
        return data


class ValidatePracticeSerializer(serializers.Serializer):
    """Serializer for validating practice."""
    
    art_id = serializers.IntegerField(required=True)
    part_id = serializers.IntegerField(required=False, allow_null=True)
    validator = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, data):
        """Validate that the art and part exist."""
        from core.models import Art, ArtParts
        
        try:
            art = Art.objects.get(id=data['art_id'])
        except Art.DoesNotExist:
            raise serializers.ValidationError({"art_id": "Art with this ID does not exist."})
        
        if 'part_id' in data and data['part_id']:
            try:
                part = ArtParts.objects.get(id=data['part_id'], art=art)
            except ArtParts.DoesNotExist:
                raise serializers.ValidationError({"part_id": "Part with this ID does not exist for this art."})
            
            # Validator is required for PEER and MENTOR validation methods
            if part.validation_method in ['PEER', 'MENTOR'] and not data.get('validator'):
                raise serializers.ValidationError({"validator": f"Validator is required for {part.get_validation_method_display()} validation."})
        
        return data 