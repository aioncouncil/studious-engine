from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, List, Union
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count, Sum, Q

from core.models import (

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]
    Art, 
    ArtParts,
    ArtStage,
    ArtMastery,
    UserArtStageProgress,
    PlayerProfile
)

User = get_user_model()

class MasteryService:
    """
    Service for managing user art mastery and progression.
    """
    
    @staticmethod
    def get_user_mastery(user, art=None):
        """
        Get a user's mastery of a specific art or all arts.
        
        Args:
            user: The User object or ID
            art: Optional Art object or ID
            
        Returns:
            ArtMastery or QuerySet: Single mastery object or QuerySet of all masteries
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        if art:
            if not isinstance(art, Art):
                try:
                    art = Art.objects.get(id=art)
                except Art.DoesNotExist:
                    raise ValueError(f"Art with ID {art} does not exist")
            
            try:
                return ArtMastery.objects.get(user=user, art=art)
            except ArtMastery.DoesNotExist:
                return None
        
        return ArtMastery.objects.filter(user=user)
    
    @staticmethod
    def update_mastery_level(mastery_id, recalculate=True):
        """
        Update the mastery level for an art mastery record.
        
        Args:
            mastery_id: The ArtMastery object or ID
            recalculate: Whether to recalculate from completed parts
            
        Returns:
            int: The updated mastery level
        """
        if not isinstance(mastery_id, ArtMastery):
            try:
                mastery = ArtMastery.objects.get(id=mastery_id)
            except ArtMastery.DoesNotExist:
                raise ValueError(f"ArtMastery with ID {mastery_id} does not exist")
        else:
            mastery = mastery_id
        
        if recalculate:
            # Recalculate based on completed parts
            mastery.recalculate_mastery_level()
        
        # Check if the mastery level qualifies for a new stage
        MasteryService.check_stage_progression(mastery)
        
        # Award XP and check virtue improvements
        MasteryService.apply_mastery_benefits(mastery)
        
        return mastery.mastery_level
    
    @staticmethod
    def check_stage_progression(mastery):
        """
        Check if the mastery level qualifies for a new stage and update progress.
        
        Args:
            mastery: The ArtMastery object
            
        Returns:
            UserArtStageProgress: The current stage progress
        """
        # Get all stages for this art
        stages = ArtStage.objects.filter(art=mastery.art).order_by('order_index')
        if not stages.exists():
            return None
        
        # Get the user's current stage progress
        current_progress = UserArtStageProgress.objects.filter(
            user=mastery.user,
            art_stage__art=mastery.art,
            is_current=True
        ).first()
        
        # If no current progress, initialize with the first stage
        if not current_progress:
            first_stage = stages.first()
            current_progress = UserArtStageProgress.objects.create(
                user=mastery.user,
                art_stage=first_stage,
                is_current=True
            )
            return current_progress
        
        # Check if the mastery level qualifies for the next stage
        current_stage = current_progress.art_stage
        next_stage = ArtStage.objects.filter(
            art=mastery.art,
            order_index__gt=current_stage.order_index
        ).order_by('order_index').first()
        
        if next_stage and mastery.mastery_level >= next_stage.mastery_threshold:
            # Complete current stage
            current_progress.is_current = False
            current_progress.completion_percentage = 100
            current_progress.save()
            
            # Create new stage progress
            new_progress = UserArtStageProgress.objects.create(
                user=mastery.user,
                art_stage=next_stage,
                is_current=True
            )
            return new_progress
        
        # Update completion percentage within the current stage
        if current_stage.order_index < len(stages) - 1:
            next_threshold = next_stage.mastery_threshold
            prev_threshold = current_stage.mastery_threshold
            stage_range = next_threshold - prev_threshold
            if stage_range > 0:
                relative_progress = mastery.mastery_level - prev_threshold
                percentage = min(100, int((relative_progress / stage_range) * 100))
                current_progress.completion_percentage = percentage
                current_progress.save()
        
        return current_progress
    
    @staticmethod
    def apply_mastery_benefits(mastery):
        """
        Apply benefits from mastery level such as XP and virtue improvements.
        
        Args:
            mastery: The ArtMastery object
            
        Returns:
            Dict: Dictionary of benefits applied
        """
        benefits = {
            'xp_awarded': 0,
            'virtue_improvements': {}
        }
        
        try:
            profile = PlayerProfile.objects.get(user=mastery.user)
            
            # Award XP based on mastery milestones
            milestones = [25, 50, 75, 100]
            for milestone in milestones:
                if mastery.mastery_level >= milestone:
                    milestone_key = f"milestone_{milestone}"
                    # Check if we've already awarded XP for this milestone
                    if not mastery.mastery_achievements or milestone_key not in mastery.mastery_achievements:
                        xp_award = milestone  # XP award scales with milestone
                        profile.experience_points += xp_award
                        benefits['xp_awarded'] += xp_award
                        
                        # Record the achievement
                        if not mastery.mastery_achievements:
                            mastery.mastery_achievements = []
                        
                        mastery.mastery_achievements.append(milestone_key)
            
            # Apply virtue improvements based on the art's virtue benefits
            if mastery.mastery_level >= 50 and mastery.art.improved_virtues:
                from studious_engine.core.services.user_service import UserService
                
                # Get player happiness
                try:
                    happiness = profile.happiness
                    
                    # Apply modest virtue improvements based on mastery level
                    # Scale factor determines how much of the art's virtue benefit to apply
                    scale_factor = mastery.mastery_level / 200  # Max 0.5 at 100% mastery
                    
                    virtue_updates = {}
                    for virtue, value in mastery.art.improved_virtues.items():
                        if hasattr(happiness, virtue):
                            current = getattr(happiness, virtue)
                            improvement = value * scale_factor
                            
                            # Only apply if it would be an improvement
                            if current < 100 - improvement:
                                virtue_updates[virtue] = current + improvement
                                benefits['virtue_improvements'][virtue] = improvement
                    
                    if virtue_updates:
                        UserService.update_happiness(profile, **virtue_updates)
                except:
                    pass
            
            profile.save()
        except PlayerProfile.DoesNotExist:
            pass
        
        # Save mastery achievements
        if benefits['xp_awarded'] > 0:
            mastery.save()
            
        return benefits
    
    @staticmethod
    def get_user_stage_progress(user, art=None):
        """
        Get a user's stage progress for one or all arts.
        
        Args:
            user: The User object or ID
            art: Optional Art object or ID
            
        Returns:
            QuerySet: QuerySet of UserArtStageProgress objects
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        query = UserArtStageProgress.objects.filter(user=user)
        
        if art:
            if not isinstance(art, Art):
                try:
                    art = Art.objects.get(id=art)
                except Art.DoesNotExist:
                    raise ValueError(f"Art with ID {art} does not exist")
            
            query = query.filter(art_stage__art=art)
        
        return query
    
    @staticmethod
    def get_mastery_summary(user):
        """
        Get a summary of a user's mastery across all arts.
        
        Args:
            user: The User object or ID
            
        Returns:
            Dict: Dictionary with mastery statistics
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        masteries = ArtMastery.objects.filter(user=user)
        
        # Calculate various statistics
        total_arts = masteries.count()
        completed_arts = masteries.filter(mastery_level=100).count()
        in_progress = total_arts - completed_arts
        
        # Calculate average mastery level
        if total_arts > 0:
            avg_mastery = sum(m.mastery_level for m in masteries) / total_arts
        else:
            avg_mastery = 0
        
        # Find most practiced art
        if total_arts > 0:
            most_practiced = max(
                masteries,
                key=lambda m: len(m.practice_history) if m.practice_history else 0
            )
            most_practiced_name = most_practiced.art.name
            most_practiced_sessions = len(most_practiced.practice_history) if most_practiced.practice_history else 0
        else:
            most_practiced_name = None
            most_practiced_sessions = 0
        
        # Find highest level art
        if total_arts > 0:
            highest_level = max(masteries, key=lambda m: m.mastery_level)
            highest_level_name = highest_level.art.name
            highest_level_value = highest_level.mastery_level
        else:
            highest_level_name = None
            highest_level_value = 0
        
        # Group masteries by taxonomy
        taxonomy_groups = {}
        for mastery in masteries:
            if mastery.art.taxonomy:
                taxonomy = mastery.art.taxonomy.name
                if taxonomy not in taxonomy_groups:
                    taxonomy_groups[taxonomy] = {
                        'count': 0,
                        'avg_level': 0,
                        'total_level': 0
                    }
                taxonomy_groups[taxonomy]['count'] += 1
                taxonomy_groups[taxonomy]['total_level'] += mastery.mastery_level
        
        # Calculate average level for each taxonomy
        for taxonomy, data in taxonomy_groups.items():
            if data['count'] > 0:
                data['avg_level'] = data['total_level'] / data['count']
            del data['total_level']  # Remove the helper field
        
        return {
            'total_arts': total_arts,
            'completed_arts': completed_arts,
            'in_progress': in_progress,
            'avg_mastery': avg_mastery,
            'most_practiced': {
                'name': most_practiced_name,
                'sessions': most_practiced_sessions
            },
            'highest_level': {
                'name': highest_level_name,
                'level': highest_level_value
            },
            'taxonomy_groups': taxonomy_groups
        } 